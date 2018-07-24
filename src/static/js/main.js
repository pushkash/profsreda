

(function($) {
	"use strict"

	
	
	// Preloader
	$(window).on('load', function() {
		$("#preloader").delay(600).fadeOut();
	});

	// Mobile Toggle Btn
	$('.navbar-toggle').on('click',function(){
		$('#header').toggleClass('nav-collapse')
	});
})(jQuery);

function csrfcookie() {
    var cookieValue = null,
        name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
	}
    return cookieValue;
};


class TestController {
	constructor(test_id) {
		this.test_id = test_id;
		this.test = {};
		this.view = new TestView();
	}

	checkSession() {
		return new Promise((r, error) => {
			return new PromiseRequest(`/tests/test/${this.test_id}/get_test_session/`).get_json()
			.then((session) => {
				this.session = session

				console.log(session)
				return r(session)
			})
			.catch(e => {
				// TODO: Обработка разных ошибок - Сейчас всегда создается новая сессия
				console.log(e)
				error(error_data)
			})
		})
	}

	create_new_session() {
		return new PromiseRequest(`/tests/test/${this.test_id}/create_test_session/`).get_json()
		.then((session) => {
			this.session = session
			return session
		})
		.catch( error_data => { 
			console.log(error_data)
			throw error_data;
		} )
	}

	getQuestionnaire() {
		return new PromiseRequest(`/tests/get_test/${this.test_id}/`).get_json()
		.then( (result) => {
			this.questions = result.test.questions
			return this.questions
		})
		.catch((e) => {
			console.log('error get_questionarrie')
			console.log(e)
		})
	}

	startTest() {
		this.getQuestionnaire()
		.then(() => this.checkSession())
		.then( (session) => {
			if (!session || session.test_session.is_finished) {
				return this.create_new_session()
			} else {
				return session
			}
		})
		.then(session => {
			let last_id = null;

			if (session.test_session.last_answered_question) {
				last_id = session.test_session.last_answered_question.id
			}

			this.view.show_tester();
			return this.showQuestion(this.findNextQuestion(last_id))
		})
		.catch(e => {
			handle_error(e)
		})
	}

	sendResponse(q_id, answer_id) {
		
		let response = {
			answer_id: answer_id
		}

		new PromiseRequest(`/tests/test_session/${this.session.test_session.id}/save_question_response/${q_id}/`).post_json(response)
		.catch((error) => {
			if (error.code == 403) {
				console.log('handle 403 error')
			} else {
				throw error
			}
		})
		.then((data) => {
			return this.checkSession()
		})
		.then((session) => {
			if (!session.test_session.is_finished)
				return this.showQuestion(this.findNextQuestion(session.test_session.last_answered_question.id))
			else {
				this.view.show_result(this.test_id)
			}
		})
		.catch(error => {
			this.handle_error(error)
		})
		
	}

	findNextQuestion(prev_id) {
		let current_index = 0;

		if (prev_id) {
			// TODO: Написать расчет следующего вопроса

			current_index = this.questions.indexOf(
				this.questions.filter(e => {
					return (e.id == prev_id)
				})[0]
			)

			current_index += 1
		} else {
			current_index = 0
		}
		return this.questions[current_index].id
	}

	showQuestion(question_id) {
		let question = this.questions.filter((e) => {
			return (e.id == question_id)
		})[0];
		if (question) {
			this.view.drawView(question, (...args) => {this.sendResponse(args[0], args[1])})
		} else {
			throw(`no question with id ${question_id} found `)
		}
	}

	showResult() {

	}

	handle_error(e) {
		this.view.show_error_view()
		console.log(e)
	}
}

class TestView {
	constructor() {
		this.progressbar = document.getElementById('test-progress')
		this.question_container = document.getElementById('test-question');
		this.answers_container = document.getElementById('answer-buttons');
	}

	showTestView() {

	}

	update_progres() {

	}

	drawView(data, answer_callback) {
		this.question_container.innerHTML = data.text
		this.answers_container.innerHTML = ''
		data.answers.forEach(answer => {
			let btn = document.createElement('button')
			btn.classList.add('btn', 'btn-default', 'btn-lg')
			btn.innerHTML = answer.text
			btn.addEventListener('click', (e) => {
				answer_callback(data.id, answer.id)
			})
			this.answers_container.appendChild(btn)
		});
	}

	show_error_view() {
		this.switch_view('test-view', 'test-error')
	}

	show_tester() {
		console.log('show tester')
		this.switch_view('test-overview', 'test-view')
	}

	start_loading() {

	}

	stop_loading() {

	}

	switch_view(view1, view2) {
		document.getElementById(view1).hidden = true;
		document.getElementById(view2).hidden = false;
	}

	show_result(test_id) {
		document.location.href = `../../../views/test/${test_id}/result/`
	}


}

class PromiseRequest {
	constructor(url) {
		this.url = url
		this.BASE_URL = window.location.origin
		
	}

	get() {
		let url = this.BASE_URL+this.url
		return new Promise( (resolve, reject) => {
			var xhr = new XMLHttpRequest();
			xhr.overrideMimeType("application/json");
			xhr.open('GET', url, true); 
			xhr.onreadystatechange = function () {
				if (xhr.readyState == 4) {
					if (xhr.status == "200") {
						resolve(xhr.responseText)
					} else {
						console.log(`error: ${url}`)
						reject(xhr.responseText)
					}
				} 
			};
			xhr.send(null);  
		})
	}

	get_json() {
		return this.get()
		.then (result => {
			try {
				return JSON.parse(result)
			} catch {
				console.log('cannot parse json')
				return {
					result: result
				}
			}
		})
		.catch (e => {
			try {
				throw JSON.parse(e)
			} catch {
				console.log('cannot parse json')
				throw {
					error: e
				}
			}
		})
	}

	post_json( data ) {
		let url = this.BASE_URL + this.url;
		let json = JSON.stringify(data);
		return new Promise((resolve, reject) => {
			var xhr = new XMLHttpRequest();
			xhr.open("POST", url, true)
			xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
			xhr.setRequestHeader('X-CSRFToken', csrfcookie());
			xhr.onreadystatechange = function() {
				if (xhr.readyState == 4) {
					if (xhr.status == "200" || xhr.status == "201") {
						resolve(xhr.responseText)
					} else {
						console.log(xhr.responseText)
						try {
							reject({
								code: xhr.status,
								body: JSON.parse(xhr.responseText)
							})
						} catch(e) {
							reject({
								code: xhr.status,
								body: xhr.responseText
							})
						}
					}
				}
			}
			xhr.send(json);
		})
	}
}

