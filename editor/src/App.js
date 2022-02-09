import React, { useReducer } from "react";
import "./style.css";

import Signin from "./Signin";
import SearchApp from "./SearchApp";

function reduce(state, action) {
  console.log({ action, state });
  switch (action.type) {
    case "SIGNIN":
      return { ...state, user: action.user };
    default:
      return state;
  }
}



function Editor({ dispatch, state }) {
  return (
    <div>
      <SearchApp />
    </div>
  );
}

export default function App({ }) {
  const [state, dispatch] = useReducer(reduce, {
    year: 1942,
    events: {},
    user: null,
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
