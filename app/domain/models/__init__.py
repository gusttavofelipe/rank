"""app/domain/models/__init__.py"""

from app.domain.models.base import CreateBaseModel, DeclarativeBase
from app.domain.models.category import CategoryModel
from app.domain.models.city import CityModel

# sem dependências de outros models
from app.domain.models.country import CountryModel

# depende de user
from app.domain.models.refresh_token import RefreshTokenModel

# depende de user e reviewed_entity
from app.domain.models.review import ReviewModel

# depende de review e user_reviewed_entity
from app.domain.models.review_response import ReviewResponseModel

# depende de city, category e user
from app.domain.models.reviewed_entity import ReviewedEntityModel
from app.domain.models.state import StateModel

# depende de user, city e category
from app.domain.models.suggestion import SuggestionModel
from app.domain.models.user import UserModel

# depende de user e reviewed_entity
from app.domain.models.user_reviewed_entity import UserReviewedEntityModel

__all__ = [
	"DeclarativeBase",
	"CreateBaseModel",
	"CountryModel",
	"StateModel",
	"CityModel",
	"CategoryModel",
	"UserModel",
	"RefreshTokenModel",
	"ReviewedEntityModel",
	"UserReviewedEntityModel",
	"ReviewModel",
	"ReviewResponseModel",
	"SuggestionModel",
]
