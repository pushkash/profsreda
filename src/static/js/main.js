

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


class TestController {
	constructor(test_id) {
		console.log(test_id)
		this.test_id = test_id;
		this.test = {};
		this.view = new TestView();
	}

	checkState() {
		let state = {
			session_id: 12,
			current: 5,
			solved: 4,
			amount: 40
		}
		this.state = state
		return new Promise((r, e) => {
			return r(state)
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
		.then(() => this.checkState())
		.then( (state) => {
			return this.showQuestion(state.current)
		})
	}

	sendAnswer(q_id, a_id) {
		console.log(`${this.test_id}, ${q_id}, ${a_id}`)

		
	}

	showQuestion(question_id) {
		console.log(`show q: ${question_id}`)
		let question = this.questions.filter((e) => {
			return (e.sort_id == question_id)
		})[0];
		if (question) {
			this.view.drawView(question, (...args) => {this.sendAnswer(args[0], args[1])})
		} else {
			handle_error('no question')
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

	drawView(data, answer_callback) {
		this.question_container.innerHTML = data.text
		console.log(data)
		this.answers_container.innerHTML = ''
		data.answers.forEach(answer => {
			let btn = document.createElement('button')
			btn.classList.add('btn', 'btn-default', 'btn-lg')
			btn.innerHTML = answer.transcript
			btn.addEventListener('click', (e) => {
				answer_callback(data.sort_id, answer.value)
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
			var xobj = new XMLHttpRequest();
			xobj.overrideMimeType("application/json");
			xobj.open('GET', url, true); 
			xobj.onreadystatechange = function () {
				if (xobj.readyState == 4 && xobj.status == "200") {
					resolve(xobj.responseText)
				}
			};
			xobj.send(null);  
		})
	}

	get_json() {
		return this.get()
		.then ((result) => {
			return JSON.parse(result)
		})
	}

	push_json( data ) {
		let url = this.BASE_URL + this.url;
		let json = JSON.stringify(data);
		new Promise((resolve, reject) => {
			let xhr = new XMLHttpRequest();
			xhr.open("POST", url, true);
			xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
			xhr.onload = function () {
				let response = JSON.parse(xhr.responseText);
				if (xhr.readyState == 4 && xhr.status == "201") {
					resolve(response)
				} else {
					reject(response)
				}
			}
			xhr.send(json);
		})
		
	}
}