from typing import Optional

from pydantic import BaseModel, field_validator, Field, PrivateAttr


class Propeller(BaseModel):
    id: Optional[int | str] = None
    rotation_speed: Optional[float] = Field(2300., gt=0)  # rpm
    blade_number: Optional[int] = Field(None, gt=0)
    tension_coefficient: Optional[float] = None  #

    _radius: PrivateAttr(None)
    _diameter: PrivateAttr(None)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value is None:
            return
        self._radius = value
        self._diameter = 2 * value

    @property
    def diameter(self):
        return self._diameter

    @diameter.setter
    def diameter(self, value):
        if value is None:
            return
        self._diameter = value
        self._radius = value / 2

    def __init__(self, **data):
        super().__init__(**data)
        self.radius = data.get('radius')
        self.diameter = data.get('diameter')

    def __str__(self):
        return f"Propeller with {self.blade_number} blades, {self.diameter} m diameter and {self.rotation_speed} rpm rotation speed."

    @classmethod
    @field_validator('_radius')
    def validate_radius(cls, v):
        assert abs(
            v - cls._diameter / 2
        ) < 1e-6, f"Radius must be half of diameter. Got {v} and diameter {cls._diameter}"
        return v

    @classmethod
    @field_validator('_diameter')
    def validate_diameter(cls, v):
        assert abs(
            v - 2 * cls._radius
        ) < 1e-6, f"Diameter must be twice the radius. Got {v} and radius {cls._radius}"
        return v


class Aerofoil(BaseModel):
    name: Optional[str] = Field(None, min_length=1)


class Wing(BaseModel):
    aerofoil: Optional[Aerofoil] = None
    oswald_efficiency_factor: Optional[float] = Field(0.85, gt=0, le=1)
    max_area: Optional[float] = Field(300, gt=0)  # m^2
    max_chord: Optional[float] = Field(2, gt=0)  # m^2

    _area: float = PrivateAttr(None)
    _aspect_ratio: float = PrivateAttr(None)
    _mean_aerodynamic_chord: float = PrivateAttr(None)
    _span: float = PrivateAttr(None)

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, value):
        if value is None:
            return
        self._area = min(value, self.max_area)
        if self._span is not None:
            self.mean_aerodynamic_chord = self._area / self._span
            self._aspect_ratio = self._span**2 / self._area
        if self._aspect_ratio is not None:
            self._span = (self._area * self._aspect_ratio)**0.5
            self.mean_aerodynamic_chord = self._area / self._span
        if self._mean_aerodynamic_chord is not None:
            self._span = self._area / self._mean_aerodynamic_chord
            self._aspect_ratio = self._span**2 / self._area

    @property
    def aspect_ratio(self):
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        if value is None:
            return
        self._aspect_ratio = value
        if self._area is not None:
            self._span = (self._area * self._aspect_ratio)**0.5
            self.mean_aerodynamic_chord = self._area / self._span
        if self._mean_aerodynamic_chord is not None:
            self._span = self._area / self._mean_aerodynamic_chord
            self._aspect_ratio = self._span**2 / self._area
        if self._span is not None:
            self.mean_aerodynamic_chord = self._area / self._span
            self._aspect_ratio = self._span**2 / self._area

    @property
    def mean_aerodynamic_chord(self):
        return self._mean_aerodynamic_chord

    @mean_aerodynamic_chord.setter
    def mean_aerodynamic_chord(self, value):
        if value is None:
            return
        self._mean_aerodynamic_chord = min(value, self.max_chord)
        if self._span is not None:
            self._area = self._mean_aerodynamic_chord * self._span
            self._aspect_ratio = self._span**2 / self._area
        if self._area is not None:
            self._span = self._area / self._mean_aerodynamic_chord
            self._aspect_ratio = self._span**2 / self._area
        if self._aspect_ratio is not None:
            self._span = (self._area * self._aspect_ratio)**0.5
            self._area = self._mean_aerodynamic_chord * self._span

    @property
    def span(self):
        return self._span

    @span.setter
    def span(self, value):
        if value is None:
            return
        self._span = value
        if self._mean_aerodynamic_chord is not None:
            self._area = self._mean_aerodynamic_chord * self._span
            self._aspect_ratio = self._span**2 / self._area
        if self._area is not None:
            self.mean_aerodynamic_chord = self._area / self._span
            self._aspect_ratio = self._span**2 / self._area
        if self._aspect_ratio is not None:
            self._area = self._span**2 / self._aspect_ratio
            self.mean_aerodynamic_chord = self._area / self._span

    def __init__(self, **data):
        super().__init__(**data)
        self.area = data.get('area')
        self.aspect_ratio = data.get('aspect_ratio')
        self.mean_aerodynamic_chord = data.get('mean_aerodynamic_chord')
        self.span = data.get('span')

    def __str__(self):
        return f"Wing with {self.area} m^2 area, {self.aspect_ratio} aspect ratio, {self.mean_aerodynamic_chord} m mean aerodynamic chord and {self.span} m span."

    def __repr__(self):
        return f"Wing(area={self.area}, aspect_ratio={self.aspect_ratio}, mean_aerodynamic_chord={self.mean_aerodynamic_chord}, span={self.span})"

    def dict(self, *args, **kwargs):
        base_dict = super().dict(*args, **kwargs)
        base_dict.update({
            'area': self.area,
            'aspect_ratio': self.aspect_ratio,
            'mean_aerodynamic_chord': self.mean_aerodynamic_chord,
            'span': self.span,
        })
        return base_dict


class Tail(BaseModel):
    S_th: Optional[float] = Field(0.5, gt=0)  # m^2
    AR_th: Optional[float] = Field(4.0, gt=0)
    t_rh: Optional[float] = Field(0.1, gt=0)  # m
    S_tv: Optional[float] = Field(0.5, gt=0)  # m^2
    AR_tv: Optional[float] = Field(4.0, gt=0)
    t_rv: Optional[float] = Field(0.1, gt=0)  # m
    lambda_quart_tv: Optional[float] = Field(0.0)  # rad
    l_lg: Optional[float] = Field(0.5, gt=0)  # m
    eta_lg: Optional[float] = Field(1.5, gt=0)


class Fuselage(BaseModel):
    length: Optional[float] = None  # m
    maximum_section_perimeter: Optional[float] = None  # m


class MassObject(BaseModel):
    name: str
    mass: Optional[float] = Field(None, gt=0)
    cg: Optional[float] = Field(None, ge=0, le=1)
    submasses: dict[str, 'MassObject'] = Field({})

    def __init__(self, **data):
        super().__init__(**data)
        self.calc_cg()

    @classmethod
    def from_mass_dict(cls, name: str, data: dict) -> 'MassObject':
        mass = data.get('total', 0)
        submasses = {}
        for key, value in data.items():
            if isinstance(value, dict):
                submasses[key] = cls.from_mass_dict(key, value)
            elif key != 'total':
                submasses[key] = cls(name=key, mass=value)
        return cls(name=name, mass=mass, submasses=submasses)

    def set_cg_from_dict(self, data: dict):
        if self.name in data:
            self.cg = data[self.name]
        for value in self.submasses.values():
            value.set_cg_from_dict(data)
        self.calc_cg()

    def calc_cg(self):
        if not self.submasses and self.cg is not None:
            return
        cg = 0
        for value in self.submasses.values():
            value.calc_cg()
            cg += value.mass * value.cg
        assert self.mass > 0, f"Mass must be greater than zero. Got {self.mass}"
        self.cg = cg / self.mass

    def __getattr__(self, item):
        if item in self.submasses:
            return self.submasses[item]
        else:
            raise AttributeError(f"No such attribute: {item}")

    def __setattr__(self, key, value):  # not tested
        if key in self.submasses:
            self.submasses[key] = value
        else:
            super().__setattr__(key, value)

    def __repr__(self):
        return f"MassObject(name={self.name}, mass={self.mass}, cg={self.cg}, submasses=\n{self.submasses})"
