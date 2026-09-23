from pydantic import BaseModel


class Mapper:
    def create_mapping(
        self,
        data_model: BaseModel,
        field_mapping: dict[str, str],
    ) -> dict:
        data = data_model.model_dump(exclude_none=True)

        mapped_data = {}

        for source_field, value in data.items():
            destination_field = field_mapping.get(source_field)

            if destination_field:
                mapped_data[destination_field] = value

        return mapped_data