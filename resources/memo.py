from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector


# API 를 만들기 위한 클래스 작성
# class(클래스) 란 변수와 함수로 구성된 묶음 !
# 클래스는 상속이 가능하다.
# API를 만들기 위한 클래스는 flask_restful 라이브러리의
# Resource 클래스를 상속해서 만들어야 한다.

class memoListResource(Resource) :
    # restful api 의 method 에 해당하는 함수 작성

    # 데이터를 업데이트하는 QPI들은 put 함수를 사용한다.
    @jwt_required()
    
    def post(self) :
        # api 실행 코드를 여기에 작성
        
        # 클라이언트에서 body 부분에 작성한 json을 
        # 받아오는 코드
        data = request.get_json()

        user_id = get_jwt_identity()

        # 받아온 데이터를 디비 저장하면 된다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''insert into memo
                    (title, date, memolist,user_id)
                    values
                    (%s, %s, %s, %s);'''
                    
            # recode 는 튜플 형태로 만든다.
            recode = (data['title'], data['date'], data['memolist'], user_id)

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

        # 숫자는 HTTPStatus 번호이다.
        return {"result" : "success"}, 200

    
    # 목록
    @jwt_required()

    def get(self) :
        # 1.클라이언트로부터 데이터를 받아온다.
        # request.args 는 딕셔너리다.
        # offset = request.args['offset']
        # offset = request.args.get('offset')


        offset = request.args['offset']
        limit = request.args['limit']
        user_id = get_jwt_identity()

        # 디비로부터 내 메모를 가져온다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들기
            query = '''select * from memo 
                        where user_id = %s
                        limit '''+offset+''' , '''+limit+'''; '''

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
        
        return {
            "result" : "success",
            "count" : len(result_list),
            "items" : result_list}, 200

#메모 정보 조회

class memoResource(Resource) :
    # 클라이언트로부터 /memo/3 이런식으로 경로를 처리하므로
    # 숫자는 바뀌므로, 변수로 처리해준다.

    def get(self, memo_id) :

        # 디비에서, memo_id 에 들어있는 값에 해당되는
        # 데이터를 select 해온다.

        try :
            connection = get_connection()

            query = '''select * 
                        from memo
                        where id = %s ;'''
            record = (memo_id, )
            
            # select 문은, dictionary = True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # select 문은, 아래 함수를 이용해서, 데이터를 가져온다.
            result_list = cursor.fetchall()

            print(result_list)

            # 중요! 디비에서 가져온 timestamp 는 
            # 파이썬의 datetime 으로 자동 변경된다.
            # 문제는! 이데이터를 json 으로 바로 보낼수 없으므로,
            # 문자열로 바꿔서 다시 저장해서 보낸다.
            i = 0
            for record in result_list :
                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['updated_at'] = record['updated_at'].isoformat()
                result_list[i]['date'] = record['date'].isoformat()
                i = i + 1                

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 503


        return {'result' : 'success' ,
                'info' : result_list[0]}

    # 데이터를 수정하는 API는 put함수를 사용
    @jwt_required()
    def put(self, memo_id) : 
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        # {
        #     "title": "검사역",
        #     "date": "2022-06-24",
        #     "memolist": "kfc"
        # }

        # body에서 전달된 데이터를 처리
        data = request.get_json()

        user_id = get_jwt_identity()
        
        # 디비 업데이트 실행코드
        try :
            # 데이터 insert
            #1. DB에 연결
            connection = get_connection()

            # 먼저 recipe_id에 들어있는 user_id가 이 사람인지 먼저 확인한다.

            query = ''' update memo
                        set title = %s, date = %s , memolist = %s
                        where id = %s and user_id = %s;'''
            record = (data['title'], data['date'], data['memolist'],memo_id, user_id)
            cursor = connection.cursor(dictionary = True)
            
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


    #삭제하는 delete함수
    @jwt_required()
    def delete(self, memo_id) :

        try :
            # 데이터 삭제
            user_id = get_jwt_identity()
            #1. DB에 연결
            connection = get_connection()
            #2. 쿼리문 만들기
            query = '''delete from memo
                        where id = %s and user_id = %s;'''

            record = ( memo_id, user_id)

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