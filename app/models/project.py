from app.factory import db


class Project(db.Model):
    """A portfolio project. Rendered on /projects (the full grid) and, when
    `featured` is set, on the home "Proyectos Destacados" scroller.

    `icon` is a filename under static/assets/projects/. The home scroller uses a
    shorter blurb (`short_description`) that falls back to `description` when empty.
    Ordering is explicit so the admin can reorder without touching code.
    """

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.Text, nullable=False, default='')
    round_icon = db.Column(db.Boolean, nullable=False, default=False)
    featured = db.Column(db.Boolean, nullable=False, default=False)
    # Shown in the "En desarrollo" section (home + /projects) with a WIP badge.
    work_in_progress = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    featured_order = db.Column(db.Integer, nullable=False, default=0)

    @property
    def home_description(self):
        return self.short_description or self.description

    def __repr__(self):
        return f'<Project {self.name}>'
