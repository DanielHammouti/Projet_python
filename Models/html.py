import webbrowser
import os

def write_html(team):
    template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Données du jeu - Joueur {team.teamID}</title>
    </head>
    <body>
        <h1>Données du jeu - Joueur {team.teamID}</h1>

        <h2>Arme</h2>
        <details>
            <summary>Unités</summary>
    """
    for unit in team.units:
        template += f"""
            <p>
                <b>ID</b>: {unit.id}<br>
                <b>Acronyme</b>: {unit.acronym}<br>
                <b>Tâche</b>: {unit.task}<br>
                <b>HP</b>: {unit.hp}<br>
                <b>Position</b>: ({unit.x}, {unit.y})<br>
            </p>
        """
    template += """
        </details>

        <h2>Bâtiments</h2>
        <details>
            <summary>Bâtiments</summary>
    """
    for building in team.buildings:
        template += f"""
            <p>
                <b>Type</b>: {type(building).__name__}<br>
                <b>Position</b>: ({building.x}, {building.y})<br>
            </p>
        """
    template += """
        </details>
    </body>
    </html>
    """
    filename = f"donnees_player_{team.teamID}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(template)
    webbrowser.open(f'file:///{os.path.abspath(filename)}')

def write_full_html(players, game_map):
    template = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Snapshot complet du jeu</title>
    </head>
    <body>
        <h1>Snapshot du jeu</h1>
    """

    for team in players:
        template += f"""
        <h2>Joueur {team.teamID}</h2>
        <details>
            <summary>Unités</summary>
            <ul>
        """
        for unit in team.units:
            template += f"""
            <li>
                <details>
                    <summary>Unité ID: {unit.id} ({unit.acronym})</summary>
                    <p>
                        <b>Tâche</b>: {unit.task}<br>
                        <b>HP</b>: {unit.hp}/{unit.max_hp}<br>
                        <b>Position</b>: ({unit.x}, {unit.y})<br>
                        <!-- Add any other relevant unit information -->
                    </p>
                </details>
            </li>
            """
        template += """
            </ul>
        </details>

        <details>
            <summary>Bâtiments</summary>
            <ul>
        """
        for building in team.buildings:
            template += f"""
            <li>
                <details>
                    <summary>Bâtiment: {type(building).__name__}</summary>
                    <p>
                        <b>HP</b>: {building.hp}/{building.max_hp}<br>
                        <b>Position</b>: ({building.x}, {building.y})<br>
                        <!-- Add any other relevant building information -->
                    </p>
                </details>
            </li>
            """
        template += """
            </ul>
        </details>
        """

    template += """
        <h2>Ressources sur la carte</h2>
        <details>
            <summary>Ressources</summary>
    """
    # Parcours des ressources dans la grille
    # On considère que game_map.grid contient des ressources
    for pos, entities in game_map.grid.items():
        for entity in entities:
            # On affiche seulement les ressources
            if hasattr(entity, 'capacity') and not hasattr(entity, 'spawnsUnits'):
                template += f"""
                <p>
                    <b>Type</b>: {entity.acronym}<br>
                    <b>Position</b>: ({entity.x}, {entity.y})<br>
                </p>
                """

    template += """
        </details>
    </body>
    </html>
    """

    filename = "full_snapshot.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(template)
    webbrowser.open(f'file:///{os.path.abspath(filename)}')
