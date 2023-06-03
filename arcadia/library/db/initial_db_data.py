from .db_types import ItemPackage, ArcadiaDataType

bind_def: ItemPackage = {
    'data_type': ArcadiaDataType.URL,
    'content': 'https://www.roboto84.dev/',
    'tags': ['roboto84']
}

bind_meta: dict = {
    'title': 'roboto84 - Full-Stack Developer',
    'description': 'Personal site of roboto84, a Full-stack developer with a strong '
                   'front-end background focused on creating engaging, accessible and performant interfaces.',
    'image_location': '/static/img/avatar/avatar.webp'
}

bind_package: tuple[ItemPackage, dict] = (bind_def, bind_meta)

initial_records: list[tuple[ItemPackage, dict]] = [bind_package]
