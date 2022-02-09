import React, { useEffect } from "react";

import {
  getAuth,
  getRedirectResult,
  signInWithRedirect,
  GoogleAuthProvider,
  onAuthStateChanged,
} from "firebase/auth";

export default function Signin({ onSignin }) {
  // TODO: cache token
  useEffect(() => {
    onAuthStateChanged(getAuth(), (user) => {
      if (user) {
        onSignin(user);
      } else {
        getRedirectResult(getAuth()).then((result) => {
          if (result == null) {
            signInWithRedirect(getAuth(), new GoogleAuthProvider());
          } else {
            onSignin(result.user);
          }
        }); 
      }
    });
  }, []);
  return <div>loading...</div>;
}
