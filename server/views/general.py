from flask import Blueprint, url_for, render_template, request, abort

mod = Blueprint('general', __name__)

@mod.route('/')
def home():
	return "<a href='/admin/'>home</a>"


