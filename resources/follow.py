from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

class FollowResource(Resource) :
    @jwt_required()
    def post(self,follow_id):
        
        #1. 클라이언트로부터 데이터를 받아온다.

        user_id = get_jwt_identity()

        #2. 데이터베이스에 친구정보 insert한다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''insert into follow
                        (follower_id, followee_id)
                        values
                        (%s,%s);'''
                    
            # recode 는 튜플 형태로 만든다.
            recode = (user_id, follow_id)

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, recode)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        return {'result' : 'success'}, 200

    @jwt_required()
    def delete(self, follow_id) :
        #1. 클라이언트로부터 데이터를 받아온다.

        user_id = get_jwt_identity()

        #2. 데이터베이스에 삭제해준다.
        try :
            # 데이터 삭제
            user_id = get_jwt_identity()
            #1. DB에 연결
            connection = get_connection()
            #2. 쿼리문 만들기
            query = '''delete from follow
                        where follower_id = %s and followee_id = %s;'''

            record = ( user_id, follow_id)

            #3. 커서를 가져온다.
            cursor = connection.cursor()
            #4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            
            #5. 커넥션을 커밋해줘야 한다. => 디비에 영구적으로 반영하라는 뜻
            connection.commit()
            #6. 자원 해제
            cursor.close()
            connection.close()

        # 정상적이지 않을때
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'error' : str(e)}, 503

        return {'result' : 'success'}, 200


class FollowListResource(Resource) :
    @jwt_required()
    def get(self) :
        #1. 클라이언트로부터 데이터 받아온다.
        offset = request.args['offset']
        limit = request.args['limit']

        user_id = get_jwt_identity()

        # 2. 디비에서 메모 가져온다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''select u.username, m.title, m.date, m.memolist, m.created_at, m.updated_at, u.id
                        from memo m
                        join follow f
                        on m.user_id = f.followee_id
                        join user u
                        on u.id = f.followee_id
                        where follower_id = %s
                        limit '''+offset+''','''+limit+''';'''

            record = (user_id, )                  

            # 3. 커서를 가져온다.
            # select를 할 때는 dictionary = True로 설정한다.
            cursor = connection.cursor(dictionary = True)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query,record)

            # 5. select 문은, 아래 함수를 이용해서, 데이터를 받아온다.
            result_list = cursor.fetchall()

            print(result_list)
            
            # 중요! 디비에서 가져온 timstamp는 
            # 파이썬의 datetime 으로 자동 변경된다.
            # 문제는 이 데이터를 json으로 바로 보낼 수 없으므로,
            # 문자열로 바꿔서 다시 저장해서 보낸다.
            i=0
            for record in result_list :
                result_list[i]['date'] = record['date'].isoformat()
                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['updated_at'] = record['updated_at'].isoformat()
                
                i = i+1
            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e), 'error_no' : 20}, 503


        return {'result' : 'success', 'count' : len(result_list),'items' : result_list}, 200
