from calendar import monthrange
from datetime import datetime, timedelta
from math import log, e
from pathlib import Path
from typing import Any, List

from app.core.config import settings


from fastapi import Depends, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import text, func

from app.core.config import settings
from app import crud
from app.core.pdf_report import PdfReport
from app.models import User, Incident
from app.api import deps
from app.schemas import ReportFilters, ReportServerMeter, ReportCamServerActivityTimeline, Company
from app import schemas, models
from app.schemas.core import QueryParams
from app.schemas.report import CamServerActivity, ReportInterventionFilters, ReportGaugeTendency, ReportServerTypeCount, ReportType, TypeCount

from app.api.api_v1.router import APIRouter


router = APIRouter()


def activity_timeline_data(db: Session, filters, company_id: int):

    servers = crud.cam_server.get_multi(db, filters={'company_id': company_id})

    sql_params = {
        'cam_server_id': None,
        'start': filters.start.strftime('%Y-%m-%d %H:%M:%S'),
        'end': filters.end.strftime('%Y-%m-%d %H:%M:%S'),
        'gap_interval': int(filters.interval.total_seconds())
    }

    response = []
    for server in servers:
        cam_server_id = server.id
        sql_params['cam_server_id'] = cam_server_id

        server_timeline = ReportCamServerActivityTimeline(
            cam_server=server,
            interval=filters.interval,
            timeline=[]
        )
        response.append(server_timeline)

        sql_series = '''
with gap as (
select
	x_axis as x_from,
	(x_axis + ':gap_interval seconds') as x_to
from
	generate_series(:start, :end, ':gap_interval seconds'::interval) as x_axis
)
        '''

        sql = f'''
{sql_series}

select
	g.x_from,
	(
	select
		count(incident.id) as i_count
	from
		incident
	left outer join camera on
		camera.id = incident.camera_id
	right outer join gap on
		incident.created_at >= gap.x_from
		and incident.created_at < gap.x_to
	where
		incident.deleted = false
		and incident.inaccurate = false
		and camera.cam_server_id = :cam_server_id
		and gap.x_from = g.x_from
	group by
		gap.x_from
	order by
		gap.x_from)
from
	gap as g
'''
        result = db.execute(text(sql), sql_params)

        for row in result:
            if row.i_count:
                y = row.i_count
            elif row.x_from > datetime.now(row.x_from.tzinfo):
                y = None
            else:
                y = 0
            server_timeline.timeline.append(CamServerActivity(
                x=row.x_from,
                y=y
            ))

    return response


def pie_count_data(db: Session, filters, company_id: int):
    query_filters = {
        'created_at': [
            ('>=', filters.start.strftime('%Y-%m-%d %H:%M:%S')),
            ('<=', filters.end.strftime('%Y-%m-%d %H:%M:%S')),
        ],
        'inaccurate': False
    }

    servers = crud.cam_server.get_multi(db, filters={'company_id': company_id})
    response = []
    for server in servers:
        cam_server_id = server.id
        query_filters['camera__cam_server_id'] = cam_server_id
        count = crud.incident.get_multi_count(db, filters=query_filters)

        response.append(ReportServerMeter(
            cam_server=server,
            value=count
        ))
    return response


def by_type_count_data(db: Session, filters, company_id: int):
    servers = crud.cam_server.get_multi(db, filters={'company_id': company_id})
    filter = {
        'created_at': [
            ('>=', filters.start.strftime('%Y-%m-%d %H:%M:%S')),
            ('<=', filters.end.strftime('%Y-%m-%d %H:%M:%S')),
        ],
        'inaccurate': False
    }
    response = []
    for server in servers:
        cam_server_id = server.id
        filter['camera__cam_server_id'] = cam_server_id
        count_query = crud.incident.get_multi_count(db, filters=filter, as_query=True)
        count_query = (
            count_query
            .with_entities(
                func.count(Incident.id).label('count'),
                func.unnest(func.string_to_array(
                    Incident.type, ',')).label('type_index')
            )
            .group_by('type_index')
        )

        counts = count_query.all()

        values = []
        for count in counts:
            values.append(TypeCount(index=count['type_index'], count=count['count']))

        response.append(ReportServerTypeCount(
            cam_server=server,
            values=values
        ))
    return response


@router.get("/activity", response_model=List[ReportCamServerActivityTimeline])
async def activity_timeline(
    db: Session = Depends(deps.get_db),
    filters: ReportFilters = Depends(ReportFilters),
    current_user: User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    """
    Incidents activity timeline by server
    """
    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id

    return activity_timeline_data(db, filters, as_company_id)


@router.get("/gauge/tendency", response_model=List[ReportGaugeTendency])
async def gauge_tendency(
    db: Session = Depends(deps.get_db),
    filters: ReportFilters = Depends(ReportFilters),
    current_user: User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    """
    Gauge meter aka. Heartbeat
    """
    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id

    servers = crud.cam_server.get_multi(db, filters={'company_id': as_company_id})

    response = []
    sql_params = {
        'cam_server_id': None,
        'start': filters.start.strftime('%Y-%m-%d %H:%M:%S'),
        'end': filters.end.strftime('%Y-%m-%d %H:%M:%S'),
        'gap_interval': int(filters.interval.total_seconds())
    }

    for server in servers:
        cam_server_id = server.id
        sql_params['cam_server_id'] = cam_server_id

        sql_series = '''
with gap as (
select
	x_axis as x_from,
	(x_axis + ':gap_interval seconds') as x_to
from
	generate_series(:start, :end, ':gap_interval seconds'::interval) as x_axis
)
        '''
        sql_select = f'''
{sql_series}

select
	g.x_from,
	(
	select
		count(incident.id) as i_count
	from
		incident
	left outer join camera on
		camera.id = incident.camera_id
	right outer join gap on
		incident.created_at >= gap.x_from
		and incident.created_at < gap.x_to
	where
		incident.deleted = false
		and incident.inaccurate = false
		and camera.cam_server_id = :cam_server_id
		and gap.x_from = g.x_from
	group by
		gap.x_from
	order by
		gap.x_from)
from
	gap as g
'''

        sql = f'''
    select
        count(res.x_from),
        avg(res.i_count),
        sum(res.i_count),
        max(res.i_count)
    from
        ({sql_select}) as res
            '''
        result = db.execute(text(sql), sql_params).first()

        if result and result.avg and result.max:
            value = (result.avg / result.max) * 100
        else:
            value = 100

        server_meter = ReportGaugeTendency(
            cam_server=server,
            interval=filters.interval,
            created=filters.start,
            value=value
        )
        response.append(server_meter)

    return response


@router.get("/gauge", response_model=List[ReportServerMeter])
async def gauge_meter(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id
    servers = crud.cam_server.get_multi(db, filters={'company_id': as_company_id})

    response = []
    for server in servers:
        cam_server_id = server.id
        end_timestamp = datetime.utcnow()
        filters = {
            'camera__cam_server_id': cam_server_id,
            'inaccurate': False
        }
        alpha_count = crud.incident.get_multi_count(db, filters={
            **filters,
            'created_at': ('>=', end_timestamp - timedelta(seconds=settings.GAUGE_ALPHA_INTERVAL))
        })
        beta_count = crud.incident.get_multi_count(db, filters={
            **filters,
            'created_at': ('>=', end_timestamp - timedelta(seconds=settings.GAUGE_BETA_INTERVAL))
        })
        gamma_count = crud.incident.get_multi_count(db, filters={
            **filters,
            'created_at': ('>=', end_timestamp - timedelta(seconds=settings.GAUGE_GAMMA_INTERVAL))
        })
        sigma_count = crud.incident.get_multi_count(db, filters={
            **filters,
            'created_at': ('>=', end_timestamp - timedelta(seconds=settings.GAUGE_GAMMA_INTERVAL))
        })
        ln = log(1/100)
        alpha_fraction = pow(e, -(alpha_count / 10) - ln)
        beta_fraction = pow(e, -(beta_count / 10) - ln)
        gamma_fraction = pow(e, -(gamma_count / 10) - ln)
        sigma_fraction = pow(e, -(sigma_count / 10) - ln)

        value = (
            settings.GAUGE_ALPHA_COEFFICIENT * alpha_fraction +
            settings.GAUGE_BETA_COEFFICIENT * beta_fraction +
            settings.GAUGE_GAMMA_COEFFICIENT * gamma_fraction +
            settings.GAUGE_SIGMA_COEFFICIENT * sigma_fraction
        )

        response.append(ReportServerMeter(
            cam_server=server,
            value=round(value, 4)
        ))
    return response


@router.get("/count", response_model=List[ReportServerMeter])
async def pie_count(
    db: Session = Depends(deps.get_db),
    filters: ReportFilters = Depends(ReportFilters),
    current_user: User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    '''
    Count incidents happened by location
    '''
    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id
    return pie_count_data(db, filters, as_company_id)


@router.get("/pdf", response_model=Any)
async def report_pdf(
    db: Session = Depends(deps.get_db),
    filters: ReportInterventionFilters = Depends(ReportInterventionFilters),
    params: QueryParams = Depends(deps.get_multi_params()),
    current_user: User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    '''
    Generate and return report PDF as attachament
    '''
    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id

    company = crud.company.get(db, as_company_id)
    created = datetime.now()

    if company:
        company = Company(**jsonable_encoder(company))

    a_second = timedelta(seconds=1)

    if filters.period and filters.period != ReportType.CUSTOM:
        # TODO parse from string or integer
        start = filters.start
        if filters.created_at_from:
            start = filters.created_at_from
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        if filters.period == ReportType.DAY:
            period = timedelta(days=1)
        elif filters.period == ReportType.WEEK:
            start = start - timedelta(days=start.weekday())
            period = timedelta(weeks=1)
        else:  # elif filters.period == ReportType.MONTH:
            start = start.replace(day=1)
            period = timedelta(days=monthrange(start.year, start.month)[1])

        filters.start = start
        filters.end = start + period - a_second
    else:
        if not filters.created_at_from:
            filters.created_at_from = (
                datetime.now()
                .replace(hour=0, minute=0, second=0, microsecond=0)
            )
        if not filters.created_at_to:
            filters.created_at_to = datetime.now()
            # TODO max 1 month period
            # filters.created_at_to = (
            #     filters.created_at_from +
            #     timedelta(
            #         days=monthrange(
            #             filters.created_at_from.year,
            #             filters.created_at_from.month + 1
            #         )[1]
            #     ) - a_second
            # )

        filters.start = filters.created_at_from
        filters.end = filters.created_at_to

    filters.created_at_from = filters.start
    filters.created_at_to = filters.end

    incidents = crud.incident.get_multi(
        db,
        company_id=as_company_id,
        filters=filters
    )
    if incidents:
        incidents = [schemas.Incident(**jsonable_encoder(incident))
                     for incident in incidents]
    if filters.camera__cam_server_id:
        server = crud.cam_server.get(db, filters.camera__cam_server_id)
    else:
        server = None
    if filters.camera_id:
        pass
    ai_types = crud.ai_type.get_multi(db)

    def type_names(types):
        names = []
        for t_index in types:
            for t in ai_types:
                if t.index == int(t_index) and t.name:
                    names.append(t.name)
        return names

    activity_timeline = activity_timeline_data(db, filters, as_company_id)

    activity = []
    for line in activity_timeline:
        timeline = [d.x for d in line.timeline]
        data_line = [d.y for d in line.timeline]
        activity.append({
            'kwargs': {
                'label': line.cam_server.location,
            },
            'x': timeline,
            'y': data_line
        })

    pie_count = pie_count_data(db, filters, as_company_id)
    pie = {'data': [], 'labels': []}
    for line in pie_count:
        pie['labels'].append(line.cam_server.location)
        pie['data'].append(line.value)

    data = {
        'created': created,
        'company': company,
        'server': server,
        'filters': filters,
        'type_names': type_names,
        'incidents': incidents,
        'activity': activity,
        'pie_location': pie
    }

    pdf = PdfReport(
        template_path=str(Path('./pdf-templates') / "report.mako"),
        css_path=str(Path('./pdf-templates') / "report.css")
    )

    attachment_filename = f'report_{created.strftime("%Y-%m-%d")}.pdf'
    pdf_file = pdf.generate(data, attachment_filename)
    return Response(pdf_file, media_type='application/octet-stream', headers={
        'Access-Control-Expose-Headers': 'Content-Disposition',
        'Content-Disposition': f'attachment; filename="{attachment_filename}"'
    })


@router.get("/by_type_count", response_model=List[ReportServerTypeCount])
async def by_type_count(
    db: Session = Depends(deps.get_db),
    filters: ReportFilters = Depends(ReportFilters),
    current_user: User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    '''
    Incidents count by detection type
    '''
    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id
    return by_type_count_data(db, filters, as_company_id)
