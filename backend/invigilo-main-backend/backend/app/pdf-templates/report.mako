<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report ${filters.start.strftime('%Y-%m-%d')} - ${filters.end.strftime('%Y-%m-%d')}</title>
</head>
<body>
    <table class="report-header">
        %if company:
        <tr>
            %if company.logo:
            <td rowspan="${4 if server else 3}" class="company-logo-cell">
                <img src="${company.logo_url}" class="company-logo" alt="${company.name}">
            </td>
            %endif
            <td colspan="2"><h2 class="company-title">${company.name}</h2></td>
        </tr>
        %endif
        <tr>
            <td class="report-label">Created:</td>
            <td class="report-value">${created.strftime('%Y-%m-%d %H:%M')}</td>
        </tr>
        <tr>
            <td class="report-label">Period:</td>
            <td class="report-value">${filters.start.strftime('%Y-%m-%d')} - ${filters.end.strftime('%Y-%m-%d')}</td>
        </tr>
        %if server:
        <tr>
            <td class="report-label">Location:</td>
            <td class="report-value">${server.location}</td>
        </tr>
        %endif
    </table>
    <table class="report-graphs">
        <tr>
            <td><img src="graph://lineplot/activity?width=7&height=3&ylabel=Incidents&title=Incidents over time&legend" /></td>
        </tr>
        <tr>
            <td><img src="graph://pie/pie_location?width=4&height=4&title=Incidents per location&legend" /></td>
        </tr>
    </table>
    <h2 class="incident-list-title">Incident list</h2>
    <table class="incident-table">
        <tr>
            <th class="incident-col-id">Sr. No</th>
            <th class="incident-col-details">Observation</th>
            <th class="incident-col-attachment">Attachment</th>
        </tr>
        <%def name="make_description(row)">
            <table class="incident-description">
                <tr>
                    <td class="description-label">UUID:</td>
                    <td class="description-value-uuid">${row.uuid}</td>
                </tr>
                <tr>
                    <td class="description-label">Violation type:</td>
                    <td>${", ".join(type_names(row.type))}</td>
                </tr>
                <tr>
                    <td class="description-label">Created at:</td>
                    <td>${row.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
                <tr>
                    <td class="description-label">Location:</td>
                    <td>${row.location}</td>
                </tr>
                <tr>
                    <td class="description-label">Count:</td>
                    <td>${row.count}</td>
                </tr>
            </table>
        </%def>
        <%def name="make_row(row, index)">
            <tr>
                <td>${index + 1}</td>
                <td>${make_description(row)}</td>
                <td><img src="${row.frame_url}" class="incident-frame"></td>
            </tr>
        </%def>
        % for row in incidents:
            ${make_row(row, loop.index)}
        % endfor
    </table>
</body>
</html>