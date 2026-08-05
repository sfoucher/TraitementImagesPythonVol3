import yaml
from typing import List, Dict, Any, Union
import html
import os
from IPython.display import display, HTML, Markdown

def is_latex_output(output_profile):
    """
    Checks if the output format is LaTeX (PDF).

    Args:
        output_format: The output format parameter (e.g., "html", "pdf").

    Returns:
        True if the output format is LaTeX (PDF), False otherwise.
    """
    return output_profile == "production"

# Get the output format from the environment variable
output_format = os.environ.get("QUARTO_OUTPUT_FORMAT", "html")
output_profile = os.environ.get("QUARTO_PROFILE", "default")

class Question:
    """Represents a question in a quiz."""

    def __init__(self, label: str, 
                 type: str, 
                 response: Union[int, List[int], str], 
                 answers: List[str] = None, 
                 section: str = None, 
                 image: str = None, 
                 alt_txt: str = None, 
                 help: str = None):
        """
        Initializes a Question object.

        Args:
            label: The question text.
            type: The question type ('uc', 'mc', or 'stat').
            response: The correct answer(s) (index for 'uc' and 'mc', string for 'stat').
            answers: The possible answers (for 'uc' and 'mc').
            section: The section the question belongs to (optional).
            image: path to an image (optional)
            alt_txt: alternative text for the image (optional)
            help_text: help text for the question (optional)
        """
        self.label = label
        self.answers = answers or []
        self.type = type
        self.response = response
        self.section = section
        self.image = image
        self.alt_txt = alt_txt
        self.help = help

    def __repr__(self):
        return f"Question(label='{self.label}', type='{self.type}', response={self.response}, answers={self.answers}, section='{self.section}', image='{self.image}', alt_txt='{self.alt_txt}', help='{self.help}')"


class Quiz:
    """Represents a quiz with multiple questions."""

    def __init__(self, yml_file: str, quizz_id: str):
        """
        Initializes a Quiz object.

        Args:
            yml_file: Path to the YAML file containing the quiz data.
            quizz_id: The ID of the quiz.
        """
        self.questions = self._load_questions(yml_file)
        self.id = quizz_id

    def _load_questions(self, yml_file: str) -> List[Question]:
        """Loads questions from a YAML file."""
        with open(yml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        questions = []
        for q_data in data:
            questions.append(Question(**q_data))
        return questions

    def __repr__(self):
        return f"Quiz(id='{self.id}', questions={self.questions})"


def build_html_response(quest: Question, i: int) -> str:
    """Builds the HTML for the answer section of a question."""
    b1 = '<div class="quizlib-question-answers">'
    b2 = ''

    if quest.type == "uc":
        b2 = '<table class="table table-sm table-striped small">'
        for j, ans in enumerate(quest.answers, 1):
            b2 += f'<tr><td><label>{ans}</label></td><td><input type="radio" name="q{i}" value="{j}"></td></tr>'
        b2 += '</table>'

    elif quest.type == "mc":
        b2 = '<table class="table table-sm table-striped small">'
        for j, ans in enumerate(quest.answers, 1):
            b2 += f'<tr><td><label>{ans}</label></td><td><input type="checkbox" name="q{i}" value="{j}"></td></tr>'
        b2 += '</table>'

    elif quest.type == "stat":
        b2 = f'<input type="text" name="q{i}">'

    b1 += b2 + '</div>'
    return b1


def build_pdf_responses(myquizz: Quiz) -> str:
    """Builds the string for the responses section in PDF format."""
    string = ""
    for quest in myquizz.questions:
        string += f"\n * {quest.label}"
        if quest.type == "uc":
            string += f"\n\t+ {quest.answers[quest.response - 1]}"
        elif quest.type == "stat":
            string += f"\n\t+ {quest.response}"
        elif quest.type == "mc":
            s2 = "\n\t+ " + "\n\t+ ".join([quest.answers[idx - 1] for idx in quest.response])
            string += s2
    return string


def render_quizz_pdf(myquizz: Quiz) -> str:
    """Renders the quiz in PDF format."""
    string = ""
    for quest in myquizz.questions:
        string += f"\n* **{quest.label}**"

        if quest.image:
            string += f"\n\n\t ![{quest.alt_txt}]({quest.image}){{width=50%}}\n"

        if quest.type == "stat":
            string += "\n\t+ ..."
        else:
            s2 = "\n\t+ " + "\n\t+ ".join(quest.answers)
            string += s2
        if quest.help:
            string += f"\n\n\t{quest.help}\n"

    questions = string
    responses = build_pdf_responses(myquizz)

    el2 = "**Réponses**\n"
    final_string = f"**Questions**\n{questions}\n\n{el2}{responses}"
    return final_string


def build_html_quizz(myquizz: Quiz) -> List[str]:
    """Builds the HTML for the entire quiz."""
    quizz_div = []
    i = 1
    for quest in myquizz.questions:
        balise = '<div class="card quizlib-question">'
        b1 = f'<div class="quizlib-question-title">{quest.label}</div>'
        bimg = ""
        if quest.image:
            bimg = f'<img src="{quest.image}" alt="{quest.alt_txt}" style="width: 50%;display: block;margin-left: auto;margin-right: auto;margin-bottom: 0.5em;margin-top: 0.5em;">'

        resp = build_html_response(quest, i)

        div_sec = ""
        if quest.help:
            div_sec = f"<div>{quest.help}</div>"

        childs = [b1]
        if quest.image:
            childs.append(bimg)
        if quest.help:
            childs.append(div_sec)
        childs.append(resp)
        balise += "".join(childs) + '</div>'
        quizz_div.append(balise)
        i += 1

    on_click = f"showResults(quizz_{myquizz.id});"
    result = f'<button type="button" onclick="{on_click}" id="buttonID">Vérifier votre résultat</button>'
    quizz_div.append(result)

    res_div = '<div id="quiz-result" class="card"><span id="quiz-percent"></span></div>'
    quizz_div.append(res_div)

    return quizz_div


def prep_jscode(myquizz: Quiz) -> str:
    """Prepares the JavaScript code for the quiz."""
    id = myquizz.id
    rep_string = ""
    for quest in myquizz.questions:
        if quest.type == "uc":
            rep_string += f"'{quest.response}',"
        elif quest.type == "stat":
            rep_string += f"'{quest.response}',"
        elif quest.type == "mc":
            string2 = f"['" + "', '".join(map(str,quest.response)) + "']"
            rep_string += string2 + ","

    rep_string = rep_string[:-1]
    rep_string = f"[{rep_string}]"

    total_code = f"""
  var quizz_{id};
  window.onload = function() {{
    quizz_{id} = new Quiz('{id}', {rep_string});
  }};"""

    js_code1 = """var Quiz=function(a,b){this.Classes=Object.freeze({QUESTION:"quizlib-question",QUESTION_TITLE:"quizlib-question-title",QUESTION_ANSWERS:"quizlib-question-answers",QUESTION_WARNING:"quizlib-question-warning",CORRECT:"quizlib-correct",INCORRECT:"quizlib-incorrect",TEMP:"quizlib-temp"}),this.unansweredQuestionText="Question sans réponse !",this.container=document.getElementById(a),this.questions=[],this.result=new QuizResult,this.answers=b;for(var c=0;c<this.container.children.length;c++)this.container.children[c].classList.contains(Quiz.Classes.QUESTION)&&this.questions.push(this.container.children[c]);if(this.answers.length!=this.questions.length)throw new Error("Number of answers does not match number of questions!")};Quiz.Classes=Object.freeze({QUESTION:"quizlib-question",QUESTION_TITLE:"quizlib-question-title",QUESTION_ANSWERS:"quizlib-question-answers",QUESTION_WARNING:"quizlib-question-warning",CORRECT:"quizlib-correct",INCORRECT:"quizlib-incorrect",TEMP:"quizlib-temp"}),Quiz.prototype.checkAnswers=function(a){void 0===a&&(a=!0);for(var b=[],c=[],d=0;d<this.questions.length;d++){var e=this.questions[d],f=this.answers[d],g=[];this.clearHighlights(e);for(var h,i=e.getElementsByClassName(Quiz.Classes.QUESTION_ANSWERS)[0].getElementsByTagName("input"),j=0;j<i.length;j++)h=i[j],"checkbox"===h.type||"radio"===h.type?h.checked&&g.push(h.value):""!==h.value&&g.push(h.value);1!=g.length||Array.isArray(f)?0===g.length&&b.push(e):g=g[0],c.push(Utils.compare(g,f))}if(0===b.length||!a)return this.result.setResults(c),!0;for(d=0;d<b.length;d++){var k=document.createElement("span");k.appendChild(document.createTextNode(this.unansweredQuestionText)),k.className=Quiz.Classes.QUESTION_WARNING,b[d].getElementsByClassName(Quiz.Classes.QUESTION_TITLE)[0].appendChild(k)}return!1},Quiz.prototype.clearHighlights=function(a){for(var b=a.getElementsByClassName(Quiz.Classes.QUESTION_WARNING);b.length>0;)b[0].parentNode.removeChild(b[0]);var c,d=[a.getElementsByClassName(Quiz.Classes.CORRECT),a.getElementsByClassName(this.Classes.INCORRECT)];for(i=0;i<d.length;i++)for(;d[i].length>0;)c=d[i][0],c.classList.remove(Quiz.Classes.CORRECT),c.classList.remove(Quiz.Classes.INCORRECT);for(var e=a.getElementsByClassName(Quiz.Classes.TEMP);e.length>0;)e[0].parentNode.removeChild(e[0])},Quiz.prototype.highlightResults=function(a){for(var b,c=0;c<this.questions.length;c++)b=this.questions[c],b.getElementsByClassName(Quiz.Classes.QUESTION_TITLE)[0].classList.add(this.result.results[c]?Quiz.Classes.CORRECT:Quiz.Classes.INCORRECT),void 0!==a&&a(this,b,c,this.result.results[c])};var QuizResult=function(){this.results=[],this.totalQuestions=0,this.score=0,this.scorePercent=0,this.scorePercentFormatted=0};QuizResult.prototype.setResults=function(a){this.results=a,this.totalQuestions=this.results.length,this.score=0;for(var b=0;b<this.results.length;b++)this.results[b]&&this.score++;this.scorePercent=this.score/this.totalQuestions,this.scorePercentFormatted=Math.floor(100*this.scorePercent)};var Utils=function(){};Utils.compare=function(a,b){if(a.length!=b.length)return!1;if(Array.isArray(a)&&Array.isArray(b)){for(var c=0;c<a.length;c++)if(a[c]!==b[c])return!1;return!0}return a===b};"""
    js_code = """
function showResults(quiz) {
    // Check answers and continue if all questions have been answered
    if (quiz.checkAnswers()) {
        var quizScorePercent = quiz.result.scorePercentFormatted; // The unformatted percentage is a decimal in range 0 - 1
        var quizResultElement = document.getElementById('quiz-result');
        quizResultElement.style.display = 'block';
        document.getElementById('quiz-percent').innerHTML = quizScorePercent.toString();

        // Change background colour of results div according to score percent
        if (quizScorePercent > 75) quizResultElement.style.backgroundColor = '#4caf50';
        else if (quizScorePercent > 50) quizResultElement.style.backgroundColor = '#ffc107';
        else if (quizScorePercent > 25) quizResultElement.style.backgroundColor = '#ff9800';
        else if (quizScorePercent > 0) quizResultElement.style.backgroundColor = '#f44336';

        // Highlight questions according to whether they were correctly answered. The callback allows us to highlight/show the correct answer
        quiz.highlightResults(handleAnswers);
    }
}

/** Callback for Quiz.highlightResults. Highlights the correct answers of incorrectly answered questions
 * Parameters are: the quiz object, the question element, question number, correctly answered flag
 */
function handleAnswers(quiz, question, no, correct) {
    if (!correct) {
        var answers = question.getElementsByTagName('input');
        for (var i = 0; i < answers.length; i++) {
            if (answers[i].type === 'checkbox' || answers[i].type === 'radio'){
                // If the current input element is part of the correct answer, highlight it
                if (quiz.answers[no].indexOf(answers[i].value) > -1) {
                    answers[i].parentNode.classList.add(Quiz.Classes.CORRECT);
                }
            } else {
                // If the input is anything other than a checkbox or radio button, show the correct answer next to the element
                var correctAnswer = document.createElement('span');
                correctAnswer.classList.add(Quiz.Classes.CORRECT);
                correctAnswer.classList.add(Quiz.Classes.TEMP); // quiz.checkAnswers will automatically remove elements with the temp class
                correctAnswer.innerHTML = quiz.answers[no];
                correctAnswer.style.marginLeft = '10px';
                answers[i].parentNode.insertBefore(correctAnswer, answers[i].nextSibling);
            }
        }
    }
}"""

    final_code = f"{js_code1}\n{js_code}\n{total_code}"
    return final_code


def render_quizz_html(myquizz: Quiz) -> str:
    """Renders the quiz in HTML format."""
    html_code = build_html_quizz(myquizz)
    js_code = prep_jscode(myquizz)

    tag1 = '<link type="text/javascript" src="libs/quizlib.1.0.1.min.js">'
    tag3 = '<link rel="stylesheet" type="text/css" src="css/quizlib.min.css">'
    tag2 = f'<script>{js_code}</script>'

    global_div = f'<div id="{myquizz.id}" class="card">'
    global_div += "".join([tag1, tag2, tag3] + html_code) + "</div>"

    string = global_div
    string = html.unescape(string)
    string = string.replace("&amp;&amp;", "&&")
    return string


def render_quizz(myquizz: Quiz) -> str:
    """Renders the quiz in either PDF or HTML format."""
    # In a real scenario, you would check the output format here
    # For this example, we'll always return HTML
    if is_latex_output(output_profile):
        return Markdown(render_quizz_pdf(myquizz))
    else:
        return HTML(render_quizz_html(myquizz))

