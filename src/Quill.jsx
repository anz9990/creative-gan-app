// import React, { useState } from "react";

// import ReactDOM from "react-dom";
import React, { Component } from "react";
import ReactQuill from "react-quill";
import QuillMention from "quill-mention";

import "react-quill/dist/quill.snow.css";

const atValues = [
  { id: 1, value: "Fredrik Sundqvist" },
  { id: 2, value: "Patrik Sjölin" }
];
const hashValues = [
  { id: 3, value: "Fredrik Sundqvist 2" },
  { id: 4, value: "Patrik Sjölin 2" }
];

// Accessing the Quill backing instance using React ref functions

class Editor extends React.Component {
  constructor (props) {
    super(props)
    this.state = { editorHtml: '', mountedEditor: false }
    this.quillRef = null;
    this.reactQuillRef = null;
    this.handleChange = this.handleChange.bind(this)
    this.handleClick = this.handleClick.bind(this)
    this.attachQuillRefs = this.attachQuillRefs.bind(this);
  }
  
  componentDidMount () {
    this.attachQuillRefs()
  }
  
  componentDidUpdate () {
    this.attachQuillRefs()
  }
  
  attachQuillRefs() {
    // Ensure React-Quill reference is available:
    if (typeof this.reactQuillRef.getEditor !== 'function') return;
    // Skip if Quill reference is defined:
    if (this.quillRef != null) return;
    
    const quillRef = this.reactQuillRef.getEditor();
    if (quillRef != null) this.quillRef = quillRef;
  }
  
  
  handleClick () {
	var quil = this.quillRef
    var range = this.quillRef.getSelection();
    let position = range ? range.index : 0;
	var xhr = new XMLHttpRequest();
	var seed = this.quillRef.getText().split()
    if(seed.length > 20) {
		seed = seed.slice(-20);
	}
	seed = seed.join(" ");
	console.log(seed);
	xhr.open('GET', "http://localhost:8899/analyze?seed='"+seed+"'", true);
	xhr.onerror = function() {alert (xhr.responseText);};
	xhr.responseType = "json"
	xhr.send();
	var response = ""
	xhr.onload = function() {
	  //console.log(xhr.response["result"]);
	  response =  xhr.response["result"];
	  console.log(response["result"])
	  quil.insertText(position, response);
    };
  }
  
  handleChange (html) {
  	this.setState({ editorHtml: html });
  }

  render () {
    return (
      <div>
        <ReactQuill 
          ref={(el) => { this.reactQuillRef = el }}
          theme={'snow'}
          onChange={this.handleChange}
		  //onKeyPress={(e) => this.handleKeyPress(e)}
          defaultValue={this.state.editorHtml}
          placeholder={this.props.placeholder} />
        <button onClick={this.handleClick}>Insert Text</button>
       </div>
     )
  }
}

export default Editor
