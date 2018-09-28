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
			this.view.init_avatar(this.test.question_count)
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
				this.view.update_progress_bar(this.test.question_count + 1)
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

	init_avatar(questions_count) {
		this.avatar = new ProgressAvatar(questions_count)
	}

	update_progres(q_number, amount) {
		document.getElementById('question_number').innerHTML = q_number;
		document.getElementById('questions_amount').innerHTML = amount;

		this.avatar.update(q_number)
		
		this.update_progress_bar((q_number-1.0)/amount*100)
	}

	update_progress_bar(percents) {
		document.getElementById('test-progress-bar').style.width = percents + '%';
	}

	drawView(data, answer_callback) {
		this.question_container.innerHTML = data.text
		this.answers_container.innerHTML = ''
		let max_width = 0;
		let btns = [];
		data.answers.forEach(answer => {
			let btn = document.createElement('button')
			btn.classList.add('btn', 'btn-default', 'btn-lg', 'answer-btn')
			btn.innerHTML = answer.text
			btns.push(btn)
			btn.addEventListener('click', (e) => {
				answer_callback(data.id, answer.id)
				btn.classList.add('btn-danger')
				btns.forEach((b) => {b.disabled = true})
				// this.answers_container
			})
			this.answers_container.appendChild(btn)
			

			if (max_width < btn.offsetWidth) max_width = btn.offsetWidth
		});
		btns.forEach((btn) => {
			btn.style.width = `${max_width}px`
		})
	}

	show_error_view() {
		document.getElementById('test-overview').hidden = true;
		this.switch_view('test-view', 'test-error')
	}

	show_tester() {
		this.switch_view('test-overview', 'test-view')
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

class ProgressAvatar {
	constructor(questions_count) {
		this.frames_count_by_type = [4,3,2,4,4,4]
		this.questions_count = questions_count
		this.rules = [1, 6, 16]
		if (questions_count > 50) {
			this.rules.push(Math.floor(questions_count * 0.5) + 1)
			this.rules.push(Math.floor(questions_count * 0.75) + 1)
			this.rules.push(Math.floor(questions_count * 0.85) + 1)
		} else {
			this.rules.push(...[21, 36, 46])
		}
	}

	/**
	 * Find frame of avatar moves
	 * @param {*} question_number the number of current question
	 */
	get_frame_info(question_number){
		if (question_number > this.questions_count || question_number < 1) new Error('unexpected question_number')
		let type_move = 0
		this.rules.forEach((rule) => {
			if (question_number >= rule) {
				type_move++
			}
		})
		let frame_number = (question_number - this.rules[type_move-1]) % this.frames_count_by_type[type_move-1] + 1
		return {type: type_move, frame: frame_number}
	}


	start_animation(question_number) {
		let type = this.get_frame_info(question_number).type;
		console.log('start animation')
		let current_frame = 1;
		let frames_numder = this.frames_count_by_type[type-1]
		this.change_frame2(type, '1')
		let timer = setInterval(() => {
			current_frame++;
			if (current_frame > frames_numder) {
				this.set_base_frame()
				clearInterval(timer)
				return;
			} else {
				this.change_frame2(type, current_frame)
			}
		}, 200)
	}



	move(question_number) {
		let length = document.getElementById('progress-bar').offsetWidth;
		let width = document.getElementById('progress-avatar').offsetWidth;
		let left = (question_number - 1) / this.questions_count  * length
		document.getElementById('progress-avatar').style.marginLeft = `${left}px`
	} 

	set_base_frame() {
		document.getElementById("progress-avatar-img").src=`../../../../static/img/game/sprite/base.png`;
	}

	change_frame(question_number) {
		let frame_info = this.get_frame_info(question_number)
		document.getElementById("progress-avatar-img").src=`../../../../static/img/game/sprite/${frame_info.type}/${frame_info.frame}.png`;
	}

	change_frame2(type, frame) {
		let frame_info = this.get_frame_info(question_number)
		document.getElementById("progress-avatar-img").src=`../../../../static/img/game/sprite/${type}/${frame}.png`;
	}

	update(question_number) {
		//this.change_frame(question_number)
		this.start_animation(question_number)
		this.move(question_number)
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
			xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
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

