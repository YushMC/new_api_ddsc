from enum import Enum

class ImageTypeEnum(str, Enum):
    LOGO= "logo"
    MAIN= "main"
    SCREENSHOT="screenshot"

class StatusEnum(str, Enum):
    UNDER_DEVELOPMENT="under_development"
    BETA="beta"
    STABLE="stable"
    LEGACY="legacy"
    ABANDONED="abandoned"
    ON_ICE="on_ice"
    ARCHIVED="archived"
    UNKNOWN="unknown"

class DurationEnum(str, Enum):
    VERY_SHORT="very_short"
    SHORT="short"
    MEDIUM="medium"
    LARGE="large"
    VERY_LARGE="very_large"
    ENDLESS="endless"
    UNKNOWN="unknown"

class CharacterEnum(str, Enum):
    SAYORI="sayori"
    MONIKA="monika"
    YURI="yuri"
    NATSUKI="natsuki"
    MC="mc"
    OC="oc"

class ModTypeEnum(str, Enum):
    TRANSLATION="translation"
    ORIGINAL="original"

class UserRolEnum(str, Enum):
    OWNER ="owner"
    EDITOR="editor"
    UPLOADER="uploader"

class CreditsTypeEnum(str, Enum):
    PORTER="porter"
    TRANSLATOR="translator"
    ORIGINAL_CREATOR="original_creator"

class NotificationTypeEnum(str, Enum):
    MOD_PENDING_REVIEW="mod_pending_review"
    MOD_APPROVED="mod_approved"
    MOD_REJECTED="mod_rejected"

class NotificationStatusEnum(str, Enum):
    UNREAD="unread"
    READ="read"