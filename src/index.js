import React from "react";
import ReactDOM from "react-dom";
//import Quill from "./Quill.jsx"
import Editor from "./Quill.jsx"

import "./styles.css";

function App() {
  return (
    <div className="App">
      <h1>Write with Creative GANs</h1>
      <h2>Start writing to see some magic happen!</h2>
      <Editor />
    </div>
  );
}

const rootElement = document.getElementById("root");
ReactDOM.render(
  <App/>, 
  rootElement
)
//ReactDOM.render(<App />, rootElement);
