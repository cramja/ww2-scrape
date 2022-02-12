import React, { useReducer } from "react";
import "./app.css";

import Signin from "./Signin";
import SearchApp from "./SearchApp";
import EditorApp from "./EditorApp";

function reduce(state, action) {
  console.log({ action, state });
  switch (action.type) {
    case "SIGNIN":
      return { ...state, user: action.user };
    case "SELECT_EVENT":
      return { ...state, eventId: action.id };
    case "UPDATE_EVENT":
      return {...state, event: action.event};
    default:
      return state;
  }
}



function Editor({ dispatch, state }) {
  return (
    <div className="app_editor">
      <SearchApp event={state.event} onSelect={(id) => dispatch({type: "SELECT_EVENT", id})} />
      <EditorApp eventId={state.eventId} onUpdate={(event) => dispatch({type:"UPDATE_EVENT", event})} />
    </div>
  );
}

export default function App({ }) {
  const [state, dispatch] = useReducer(reduce, {
    user: null,

    eventId: null
  });

  return (
    <>
      {state.user == null ? (
        <Signin onSignin={(user) => dispatch({ type: "SIGNIN", user })} />
      ) : (
        <Editor dispatch={dispatch} state={state} />
      )}
    </>
  );
}
