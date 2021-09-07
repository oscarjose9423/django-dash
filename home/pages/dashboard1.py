import dash_html_components as html

page = html.Div(
    className='row card', 
    children=
    [
        html.Div(
        className='card-content', 
        children=

        [
        #Title
            html.Div(
                className='col s12', 
                children=
                [
                    html.Span(
                        className='card-title', 
                        children='Consumer expenditures'),
                ]
            )
        ]
        )
    ]
)