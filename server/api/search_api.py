from flask import Blueprint, request, jsonify, abort

mod = Blueprint('search_api', __name__)



@mod.route('/<params>', methods=['GET'])
def search(params):
    print('in search')
    print(params)
    return jsonify({'s':'s'})

# from server.methods.general_utils.string_cleanup import remove_articles, remove_punctuation
# from sqlalchemy import and_, or_


# class Search:

    

#     def search(self, search_query, query_type, search_cols):

#         #remove all punctuation from searhc query. remove any articles
#         search_query = remove_articles(search_query)
#         search_query = remove_punctuation(search_query)

#         search_query = '%'.join(search_query.split(' '))
#         print('search_query: {}'.format(search_query))

#         results = None
#         if query_type == 'ILIKE':
#             results = self.ilike_query(search_query, search_cols)
#         else:
#             raise "Search type not supported."

#         return results

        
# # returns matching rows with ilike function
#     # search_query is a list of the search term which is split by spaces
#     # search_cols is a list of columns you want to search
#     @classmethod
#     def ilike_query(self, search_query, search_cols):

#         filter_criteria = ()

#         for col in search_cols:
#             if col in self.__table__.columns:
#                 filter_criteria += (getattr(self, col).ilike('%{}%'.format(search_query)), )

#         return self.query.filter(or_(*filter_criteria)).all()




#     