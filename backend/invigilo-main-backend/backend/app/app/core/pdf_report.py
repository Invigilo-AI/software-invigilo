import logging
from io import BytesIO
from typing import Dict, List, Union

from weasyprint import HTML, CSS, default_url_fetcher
from weasyprint.text.fonts import FontConfiguration

from weasyprint.logger import LOGGER as weayprint_logger
from mako.template import Template

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sbn
from urllib.parse import urlparse, parse_qs


class LoggerFilter(logging.Filter):
    def filter(self, record):
        # if record.level == logging.INFO:
        print(record.getMessage())
        return False


class PdfReport:
    def __init__(
        self,
        template_path: str,
        css_path: Union[str, List[str]] = None,
        with_logging: bool = False
    ) -> None:
        self.font_config = FontConfiguration()
        self.template = Template(filename=template_path)
        self.stylesheets = None

        self.data = None

        if not css_path:
            pass
        elif isinstance(css_path, list):
            self.stylesheets = []
            for path in css_path:
                if path:
                    self.stylesheets.append(CSS(path))
        else:
            self.stylesheets = [CSS(css_path)]

        if with_logging:
            self.logging()

    def logging(self):
        # TODO use to generate progress one of 7 steps
        weayprint_logger.setLevel(logging.DEBUG)
        logger = logging.getLogger('weasyprint')
        logger.addFilter(LoggerFilter())

        logger.handlers = []
        logger.addHandler(logging.FileHandler('./weasyprint.log'))

    def url_fetcher(self, url):
        url_parsed = urlparse(url)
        if url_parsed.scheme == 'graph':
            graph_type = url_parsed.hostname
            data_key = url_parsed.path[1:]
            params = parse_qs(url_parsed.query, keep_blank_values=True)

            for key, value in params.items():
                params[key] = value[0] if len(value) == 1 else True

            return dict(
                file_obj=self.generate_graph(graph_type, self.data[data_key], params),
                mime_type='image/png'
            )
        return default_url_fetcher(url)

    def generate_graph(self, graph_type, data, params: dict = {}):
        graph_fn = None
        colors = sbn.color_palette('pastel')
        sbn.set_palette('pastel')
        if graph_type == 'pie':
            graph_fn = lambda data: plt.pie(data.get('data'), labels=data.get('labels'), colors=colors, labeldistance=None, **data.get('kwargs', {}))
        if graph_type == 'plot':
            graph_fn = lambda data: plt.plot(data.get('x'), data.get('y'), colors=colors, **data.get('kwargs', {}))
        elif graph_type == 'lineplot':
            graph_fn = lambda data: sbn.lineplot(x=data.get('x'), y=data.get('y'), **data.get('kwargs', {}))
        if not graph_fn:
            return None

        buf = BytesIO()

        if 'width' in params and 'height' in params:
            plt.figure(figsize=(int(params['width']), int(params['height'])))

        if isinstance(data, list):
            for line in data:
                graph_fn(line)
        else:
            graph_fn(data)

        if 'ylabel' in params:
            plt.ylabel(params['ylabel'])
        if 'xlabel' in params:
            plt.xlabel(params['xlabel'])
        if 'title' in params:
            plt.title(params['title'])
        if 'legend' in params:
            plt.legend()
        plt.tick_params(axis='x', labelsize=10, rotation=45)

        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        return buf

    def generate(self, data: Dict = None, file_name: str = 'report.pdf', as_return: bool = True):
        self.data = data if data else {}
        self.data['_file_name'] = file_name

        html = HTML(
            string=self.template.render(**self.data),
            url_fetcher=self.url_fetcher
        )

        pdf_file = html.write_pdf(
            target=file_name if not as_return else None,
            stylesheets=self.stylesheets,
            font_config=self.font_config,
            optimize_size=('fonts', 'images')
        )

        return pdf_file
