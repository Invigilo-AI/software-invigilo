# Invigilo API

Requirements:

- [Poetry](https://python-poetry.org/)
- Python 3.9
- Postgres SQL 14

## PDF reports

Used library [WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/)

- Install need dependence libraries on the machine
- Uses [Mako](https://www.makotemplates.org/) template for reports
- Edit report template `./pdf-templates/report.mako` and CSS styles `./pdf-templates/report.css`
- Uses [matplotlib](https://matplotlib.org/) for drawing graphs

Define graph via custom url schema `<img src="graph://lineplot/activity?width=7&height=3&ylabel=Incidents&title=Incidents over time&legend" />`.
Where hostname `lineplot` is graph type, and can be extended in `PdfReport.generate_graph`.
The path `/activity` is the key for Mako data, already formatted as graph data.
And using query params can be provided specific settings for graph.

## Install

Copy configuration file for the environment:

```
cp .env.example .env
```
Update variables in `.env`
- Update `PROJECT_NAME` to distinguish your environments
- Add hosts for CORS origins in `BACKEND_CORS_ORIGINS`
- Generate `SECRET_KEY` for `JWT` tokens
- Auto creation of first `superuser` set the `FIRST_SUPERUSER` and `FIRST_SUPERUSER_PASSWORD`
- Setup the `POSTGRES_*` configuration for database access
- Setup the `SMTP_*` configuration and `EMAILS_FROM_EMAIL` for sender address
- Get hands on Telegram Bot access token and update `TELEGRAM_ACCESS_TOKEN`
- Setup the Telegram Bot Webhook with any generated hash as `TELEGRAM_WEBHOOK_TOKEN` as `https://api.telegram.org/botTELEGRAM_ACCESS_TOKEN/setWebhook?url=https://example.com/api/v1/hooks/telegram/TELEGRAM_WEBHOOK_TOKEN`
- Setup the `S3_*`
- Setup `AWS_*` credentials to uploading to S3
- Update if need `NOTIFICATION_TIME_WINDOW` for the timeout of intervention to be marked as `acknowledged` or `inaccurate`
- Update if need `CAMERA_ACTIVITY_INTERVAL` that is used as interval for calculation of cameras activity percentage

## Deploy on AWS EC2
Pull latest version from git `https://gitlab.com/ion.moraru1/invigilo`
Run to rebuild the containers
```
sudo docker-compose up --build --force-recreate -d
```

Troubleshooting guide for deployment can be found [here](https://docs.google.com/document/d/1RREnSx3l4AGVlnroe9eB0n5eQxlGqM3yYZEVFNu99NY/edit)