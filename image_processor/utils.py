# utils.py
def generate_css_goal_and_cards(template_url: str) -> str:
    return f"""
    .overlay {{
        position: relative;
        width: 1920px;
        height: 1920px;
        font-family: 'Proxima Nova', sans-serif;
        color: white;
        background-image: url('{template_url}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        text-transform: uppercase;
        overflow: hidden;
    }}

    .player-image {{
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 1750px;
        height: 1750px;
        object-fit: contain;
        object-position: bottom center;
    }}
    .player-name {{
        position: absolute;
        bottom: 150px;
        right: 30px;
        transform: rotate(-90deg) translateX(100%);
        transform-origin: bottom right;
        font-size: 40px;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }}
    """


def generate_css_fixture_and_game_status(template_url: str) -> str:
    return f"""
    body, html {{
        margin: 0;
        padding: 0;
    }}

    .overlay {{
        position: relative;
        width: 1920px;
        height: 1920px;
        font-family: 'Proxima Nova', sans-serif;
        color: white;
        background-image: url('{template_url}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        text-transform: uppercase;
    }}

    .hashtags {{
        position: absolute;
        top: 630px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 46px;
        font-weight: 700;
        color: white;
        white-space: nowrap;
        letter-spacing: 2px;
    }}

    .hashtag-symbol {{
        color: #0b52a7;
        letter-spacing: 10px;
    }}

    .hashtag {{
        display: inline-block;
    }}

    .hashtag + .hashtag {{
        margin-left: 20px;
    }}

    .team-container {{
        position: absolute;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 350px;
        height: 700px;
        top: 710px;
    }}

    .team-container.home {{
        left: 452px;
    }}

    .team-container.away {{
        right: 452px;
    }}

    .team-logo {{
        width: 350px;
        height: 350px;
    }}

    .team-name {{
        margin-top: 170px;
        font-size: 60px;
        font-weight: 700;
        white-space: nowrap;
        text-align: center;
        letter-spacing: 10px;
        word-break: normal;
        overflow-wrap: normal;
    }}

    .date {{
        position: absolute;
        bottom: 276px;
        right: 101px;
        font-size: 60px;
        text-align: right;
        font-weight: 700;
        color: #000;
    }}

    .time {{
        position: absolute;
        bottom: 186px;
        right: 101px;
        font-size: 60px;
        text-align: right;
        font-weight: 700;
        color: #000;
    }}

    .match-stadium {{
        position: absolute;
        bottom: 95px;
        right: 102px;
        font-size: 60px;
        text-align: right;
        font-weight: 700;
        color: #0b52a7;
    }}

    .team-result {{
        font-size: 350px;
        font-weight: 700;
        color: #ffd700;
    }}
    """
