

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
				return new PromiseRequest(`/tests/test/${this.test_id}/create_test_session/`).get_json()
				.then((session) => {
					this.session = session
					console.log(session)
					return r(session)
				})
				.catch( e => { error(e)} )
			})
		})
	}

	getQuestionnaire() {
		return new PromiseRequest(`/tests/get_test/${this.test_id}/`).get_json()
		.then( (result) => {
			this.questions = result.test.questions
		})
	}

	startTest() {
		this.getQuestionnaire()
		.then(() => this.checkSession())
		.then( (session) => {
			return this.showQuestion(this.findNextQuestion(session.test_session.last_answered_question.id))
		})
		.catch(e => {
			handle_error(e)
		})
	}

	sendResponse(answer_id) {
		
		let response = {
			answer_id: answer_id
		}
		new PromiseRequest(`/tests/test_session/${this.session.test_session.id}/save_question_response/${this.test_id}/`).post_json(response)
		.catch((error) => {
			if (error.code == 403) {
				console.log('handle 403 error')
			} else {
				throw this.handle_error(error.body)
			}
		})
		.then((data) => {
			return this.checkSession()
		})
		.then((session) => {
			return this.showQuestion(this.findNextQuestion(session.test_session.last_answered_question.id))
		})
		

		// this.checkSession()
		// .then(session => {console.log(session)})

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
		console.log(current_index)
		return this.questions[current_index].id
	}

	showQuestion(question_id) {
		let question = this.questions.filter((e) => {
			return (e.id == question_id)
		})[0];
		if (question) {
			this.view.drawView(question, (...args) => {this.sendResponse(args[0])})
		} else {
			throw(`no question with id ${question_id} found `)
		}
	}

	showResult() {

	}

	handle_error(e) {
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

	drawView(data, answer_callback) {
		this.question_container.innerHTML = data.text
		console.log(data)
		this.answers_container.innerHTML = ''
		data.answers.forEach(answer => {
			let btn = document.createElement('button')
			btn.classList.add('btn', 'btn-default', 'btn-lg')
			btn.innerHTML = answer.text
			btn.addEventListener('click', (e) => {
				answer_callback(answer.id)
			} )
			this.answers_container.appendChild(btn)
		});
	}

	show_error_view() {

	}

	start_loading() {

	}

	stop_loading() {

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
			return JSON.parse(result)
		})
		.catch (e => {
			throw JSON.parse(e)
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
						reject({
							code: xhr.status,
							body: JSON.parse(xhr.responseText)
						})
					}
				}
			}
			xhr.send(json);
		})

		// return new Promise((resolve, reject) => {
		// 	let xhr = new XMLHttpRequest();
		// 	xhr.open("POST", url, true);
		// 	xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
		// 	xhr.onreadystatechange = function () {
		// 		let response = JSON.parse(xhr.responseText);
		// 		console.log('changed')
		
		// 	}
		// 	xhr.send(json);
		// })
		
	}
}

