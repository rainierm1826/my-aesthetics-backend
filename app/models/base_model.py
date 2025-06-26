from sqlalchemy import Enum


sex_enum = Enum("male", "female", "others", name="sex_enum")