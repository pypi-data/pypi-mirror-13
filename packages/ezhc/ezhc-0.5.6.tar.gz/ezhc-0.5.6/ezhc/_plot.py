
import os
import pandas as pd
import datetime as dt
import uuid
from IPython.display import HTML


from _config import JS_LIBS_ONE, JS_LIBS_TWO, JS_SAVE
from scripts import JS_JSON_PARSE
from _img import embed_img



def html(options, lib='hicharts', dated=True, save=False, save_name=None,
         html_init=None, js_option_postprocess=None, js_extra=None, callback=None, footer=None):
    """
    save=True will create a standalone HTML doc under localdir/saved (creating folfer save if necessary)
    """

    def json_dumps(obj):
        return pd.io.json.dumps(obj)


    chart_id = str(uuid.uuid4()).replace('-', '_')

    _options = dict(options)
    _options['chart']['renderTo'] = chart_id+'container_chart'
    json_options = json_dumps(_options).replace('__uuid__', chart_id)


    # HTML
    html_init = html_init if html_init else '<div id="__uuid__"><div id="__uuid__container_chart"></div></div>'
    footer = footer if footer else ''
    
    html = html_init + footer
    html = html.replace('__uuid__', chart_id)


    # JS
    js_option_postprocess = js_option_postprocess.replace('__uuid__', chart_id) if js_option_postprocess else ''
    js_extra = js_extra.replace('__uuid__', chart_id) if js_extra else ''
    callback = ', '+callback.replace('__uuid__', chart_id) if callback else ''

    js_option = """
    var options = %s;
    %s
    %s
    window.opt = $.extend(true, {}, options);
    console.log('Highcharts/Highstock options accessible as opt');
    """ % (json_options, JS_JSON_PARSE, js_option_postprocess)


    if lib=='highcharts':
        js_call = 'window.chart = new Highcharts.Chart(options%s);' % (callback)
    elif lib=='highstock':
        js_call = 'window.chart = new Highcharts.StockChart(options%s);' % (callback)

    js_debug = """
    console.log('Highcharts/Highstock chart accessible as chart');
    """

    js = """<script>
    // nbconvert loads jquery.min.js  and require.js and at the top of the .ipnb
    // then to make jquery available inside a require module
    // the trick is http://www.manuel-strehl.de/dev/load_jquery_before_requirejs.en.html
    define('jquery', [], function() {
    return jQuery;
    });

    require(%s, function() {
        require(%s, function() {
            %s
            %s
            %s
            %s
        });
    });
    </script>""" % (JS_LIBS_ONE, JS_LIBS_TWO, js_option, js_extra, js_call, js_debug)



    # embed img (paths or url)
    contents = embed_img(html+js)

    # save
    if save==True:
        if not os.path.exists('saved'):
            os.makedirs('saved')
        tag = save_name if save_name else 'plot'
        dated = dt.datetime.now().strftime('_%Y%m%d_%H%M%S') if dated else ''
        with open(os.path.join('saved', tag+dated+'.html'), 'w') as f:
            contents = """
            <script src="%s"></script>
            <script src="%s"></script>
            %s
            """ % (JS_SAVE[0], JS_SAVE[1], contents)
            f.write(contents)

    return html+js





def plot(options, lib='hicharts', dated=True, save=False, save_name=None,
         html_init=None, js_option_postprocess=None, js_extra=None, callback=None, footer=None):
    contents = html(options, lib, dated, save, save_name, html_init, js_option_postprocess, js_extra, callback, footer)
    return HTML(contents)



