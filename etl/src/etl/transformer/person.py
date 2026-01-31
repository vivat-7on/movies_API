from etl.dto.dto import PersonDTO
from etl.es.model import EsPerson


def transform_person(person: PersonDTO) -> EsPerson:
    return EsPerson(
        id=person.id,
        name=person.full_name,
        )
