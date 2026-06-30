from app.factory import db
from app.models.project import Project


class ProjectRepository:

    @staticmethod
    def get_all():
        """All projects ordered for the /projects grid (WIP ones get a badge)."""
        return Project.query.order_by(Project.sort_order, Project.id).all()

    @staticmethod
    def get_featured():
        """Projects shown on the home scroller, in their own order."""
        return (Project.query
                .filter_by(featured=True)
                .order_by(Project.featured_order, Project.id)
                .all())

    @staticmethod
    def get_by_id(project_id):
        return Project.query.get(project_id)

    @staticmethod
    def add(project):
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def save():
        db.session.commit()

    @staticmethod
    def delete(project):
        db.session.delete(project)
        db.session.commit()

    @staticmethod
    def count():
        return Project.query.count()
