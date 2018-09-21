

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
		return new Promise((resolve, reject) => {
			return new PromiseRequest(`/tests/test/${this.test_id}/get_test_session/`).get_json()
			.then((session) => {
				this.session = session
				return resolve(session)
			})
			.catch(error_data => {
				reject(error_data)
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

	getTest() {
		return new PromiseRequest(`/tests/get_test_info/${this.test_id}/`).get_json()
		.then( (result) => {
			this.test = result.test
			return this.test
		})
		.catch((error) => {
			throw error
		})
	}

	startTest() {
		this.getTest()
		.then(() => this.checkSession())
		.catch(error => {
			if (error.code != 403) throw {code: 404, body: 'cannotfind test'}
		})
		.then( (session) => {
			if (!session || session.test_session.is_finished) {
				return this.create_new_session()
			} else {
				return session
			}
		})
		.then(session => {
			this.view.show_tester();
			return this.showQuestion(session.test_session.next_question_to_answer.id)
		})
		.catch(error => {
			this.handle_error(error)
		})
	}

	sendResponse(q_id, answer_id) {		
		let response = {
			answer_id: answer_id
		}
		new PromiseRequest(`/tests/test_session/${this.session.test_session.id}/save_question_response/${q_id}/`).post_json(response)
		.catch((error) => {
			if (error.code != 403) throw error
		})
		.then(() => this.checkSession())
		.then((session) => {
			if (!session.test_session.is_finished)
				return this.showQuestion(session.test_session.next_question_to_answer.id)
			else {
				this.view.show_result(this.test_id)
			}
		})
		.catch(error => {
			this.handle_error(error)
		})
	}

	showQuestion(question_id) {
		this.view.update_progres(
			this.session.test_session.count_answered_questions + 1,
			this.test.question_count)
		// let question = this.questions.filter((e) => {
		// 	return (e.id == question_id)
		// })[0];
		let question = this.session.test_session.next_question_to_answer
		
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

	update_progres(q_number, amount) {
		document.getElementById('question_number').innerHTML = q_number;
		document.getElementById('questions_amount').innerHTML = amount;
		this.update_progress_bar((q_number-1.0)/amount*100)
	}

	update_progress_bar(percents) {
		document.getElementById('test-progress-bar').style.width = percents + '%';
	}

	drawView(data, answer_callback) {
		this.question_container.innerHTML = data.text
		this.answers_container.innerHTML = ''
		let max_width = 0;
		data.answers.forEach(answer => {
			let btn = document.createElement('button')
			btn.classList.add('btn', 'btn-default', 'btn-lg', 'answer-btn')
			btn.innerHTML = answer.text
			btn.addEventListener('click', (e) => {
				answer_callback(data.id, answer.id)
			})
			this.answers_container.appendChild(btn)
			console.log(btn.offsetWidth)
		});

		


	}

	show_error_view() {
		document.getElementById('test-overview').hidden = true;
		this.switch_view('test-view', 'test-error')
	}

	show_tester() {
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
		this.update_progress_bar(100)
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
						reject({
							code: xhr.status,
							error_message: xhr.responseText
						})
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
				return {
					result: result
				}
			}
		})
		.catch (e => {
			try {
				throw JSON.parse(e)
			} catch {
				throw e
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

