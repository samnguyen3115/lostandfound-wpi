from datetime import datetime, timezone
from typing import Optional
from app import db, login
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


# Association Table for Tags and Posts
postTags = db.Table(
    'postTags',
    db.metadata,
    sqla.Column('post_id', sqla.Integer, sqla.ForeignKey('post.id', ondelete='CASCADE'), primary_key=True),
    sqla.Column('tag_id', sqla.Integer, sqla.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)


# User Model
class User(UserMixin, db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    email: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120), unique=True, nullable=False)
    firstname: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), nullable=False)
    lastname: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), nullable=False)
    wpi_id: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(9), unique=True)
    phonenum: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(11), unique=True, nullable=True)
    password_hash: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))
    posts: sqlo.WriteOnlyMapped[list["Post"]] = sqlo.relationship("Post", back_populates='writer', cascade="all, delete-orphan")
    type: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10), nullable=False, default="user")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return self.password_hash is not None and check_password_hash(self.password_hash, password)
    
    def total_posts(self):
        return db.session.query(sqla.func.count(Post.id)).filter(Post.userid == self.id).scalar()




# Tag Model
class Tag(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50), unique=True, nullable=False)
    category: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20), nullable=False)  

    def __repr__(self):
        return f"<Tag id={self.id} name={self.name} category={self.category}>"


# Post Model
class Post(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    userid: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.id, ondelete="CASCADE"), index=True)
    title: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(80), nullable=False)
    type: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10), nullable=False)
    left_location: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(150), nullable=True)
    reward: sqlo.Mapped[Optional[int]] = sqlo.mapped_column(sqla.Integer, nullable=True)
    timestamp: sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default=lambda: datetime.now(timezone.utc))

    # Relationships for color and building tags
    color_tag_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('tag.id'), nullable=False)
    color_tag: sqlo.Mapped["Tag"] = sqlo.relationship(
        "Tag",
        foreign_keys=[color_tag_id],
        primaryjoin="and_(Post.color_tag_id == Tag.id, Tag.category == 'color')",
        lazy="joined"
    )

    building_tag_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('tag.id'), nullable=False)
    building_tag: sqlo.Mapped["Tag"] = sqlo.relationship(
        "Tag",
        foreign_keys=[building_tag_id],
        primaryjoin="and_(Post.building_tag_id == Tag.id, Tag.category == 'building')",
        lazy="joined"
    )
    report: sqlo.Mapped[list["Report"]] = sqlo.relationship("Report", backref='post', cascade='all, delete-orphan')
    writer: sqlo.Mapped["User"] = sqlo.relationship("User", back_populates="posts")
    image = db.relationship('ImageStore', backref='post', uselist=False,cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Post id={self.id} title={self.title}>"
    
    
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    get_reported = db.Column(db.Boolean, nullable=False,default=False)
    report_reason = db.Column(db.String(200), nullable=False,default = "Not reported")

    def __repr__(self):
        return f"<Report id={self.id} post_id={self.post_id} reporter_id={self.reporter_id}>"



# Image Store Model
class ImageStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    image_type = db.Column(db.String(50), nullable=True)

class Building(db.Model):
    building_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    count = db.Column(db.Integer)
    title = db.Column(ARRAY(db.String(200)))
    body = db.Column(ARRAY(db.String(200)))
    theme_image_link = db.Column(db.String(50))
    image_link = db.Column(ARRAY(db.String(50)))
    
    def get_name(self):
        return self.name
    def get_count(self):
        return self.count
    def get_place(self):
        return self.title
    def get_body(self):
        return self.body
    def get_image(self):
        return self.image_link
    def get_theme(self):
        return self.theme_image_link