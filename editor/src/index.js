import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";

import App from "./App";

import { initializeApp } from "firebase/app";


const firebaseConfig = {
  apiKey: "AIzaSyCOrhuHOLAMwlEwQRllDxf3U8zP9K2PVgQ",
  authDomain: "event-editor.firebaseapp.com",
  projectId: "event-editor",
  storageBucket: "event-editor.appspot.com",
  messagingSenderId: "852951075228",
  appId: "1:852951075228:web:240e27a00b9f94cacea059",
};
const firebaseApp = initializeApp(firebaseConfig);

ReactDOM.render(
    <App firebaseApp={firebaseApp} />,
  document.getElementById("root")
);
