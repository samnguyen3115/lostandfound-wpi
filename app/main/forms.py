from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField,BooleanField,IntegerField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import  DataRequired,Length
from flask_wtf.file import FileField, FileAllowed
from wtforms.widgets import ListWidget, CheckboxInput
from .models import Tag, Post

from app import db
import sqlalchemy as sqla

class FoundPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),Length(min=1, max=80)])
    color_tag = QuerySelectField(
        'Color Tag',
        query_factory=lambda: db.session.scalars(sqla.select(Tag).where(Tag.category == "color").order_by(Tag.name)),  
        get_label=lambda tag: tag.name,  
        allow_blank=True
    )

    # Dropdown for Building Tag
    building_tag = QuerySelectField(
        'Building Tag',
        query_factory=lambda: db.session.scalars(sqla.select(Tag).where(Tag.category == "building").order_by(Tag.name)),  
        get_label=lambda tag: tag.name,  
        allow_blank=True,  
        blank_text=''  
    )
    left_location = TextAreaField('Where did you left the item?', validators=[DataRequired(),Length(min=1, max=150)])

    image = FileField('Please add an image of the item', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])    
    submit = SubmitField('Post')
    
class LostPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),Length(min=1, max=80)])
    color_tag = QuerySelectField(
        'Color Tag',
        query_factory=lambda: db.session.scalars(sqla.select(Tag).where(Tag.category == "color").order_by(Tag.name)),  
        get_label=lambda tag: tag.name,  
        allow_blank=True
    )

    # Dropdown for Building Tag
    building_tag = QuerySelectField(
        'Building Tag',
        query_factory=lambda: db.session.scalars(sqla.select(Tag).where(Tag.category == "building").order_by(Tag.name)),  
        get_label=lambda tag: tag.name,  
        allow_blank=True,  
        blank_text=''  
    )
    reward = IntegerField('Reward')
    description = TextAreaField('Description', validators=[DataRequired(),Length(min=1, max=150)])
    image = FileField('Please add an image of the item', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])    
    submit = SubmitField('Post')
    
class FilterForm(FlaskForm):
    color_filter = SelectField('Filter by color', choices=[
        ('',''),
        ('1', 'Red'),
        ('2', 'Orange'),
        ('3', 'Yellow'),
        ('4', 'Green'),
        ('5', 'Blue'),
        ('6', 'Purple'),
        ('7', 'Pink'),
        ('8', 'Brown'),
        ('9', 'Black'),
        ('10', 'White'),
        ('11', 'Gray')
    ])
    building_filter = SelectField(
    'Filter by building',
    choices=[
        ('', ''),
        ('12', 'Alden Memorial'),
        ('13', 'Atwater Kent Lab'),
        ('14', 'Fuller Lab'),
        ('15', 'Gordon Library'),
        ('16', 'Goddard Hall'),
        ('17', 'Higgins Lab'),
        ('18', 'Kaven Hall'),
        ('19', 'Olin Hall'),
        ('20', 'Rubin Campus Center'),
        ('21', 'Salisbury Labs'),
        ('22', 'Stratton Labs'),
        ('23', 'Innovation Studio'),
        ('24', 'Morgan Dining Hall'),
        ('25', 'Sports and Recreation Center'),
        ('26', 'Harrington Auditorium'),
        ('27', 'Unity Hall'),
        ('28', 'Bartlett Center'),
        ]
    )

    submit = SubmitField('Filter')
    submit2 = SubmitField('Refresh')

    