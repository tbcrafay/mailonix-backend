"""Saare contracts ki common config.

frozen=True   -> bani hui object ki field badli nahi ja sakti. Isi se qaida #1
                 ("check email ko badalta nahi") code mein khud lagu hota hai.
                 Badalna ho to model_copy(update={...}) se nayi copy banao.
extra=forbid  -> ghalat ya naya field name foran error deta hai, chupke se
                 contract nahi badalta.
Lists ki jagah tuple istemal hui hain taake andar ki cheezein bhi na badlen.
"""

from pydantic import BaseModel, ConfigDict

CONTRACT_VERSION = "1.0"


class Contract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=False)
