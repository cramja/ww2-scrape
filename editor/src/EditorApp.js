import React, { useState, useEffect } from "react";
import { getFirestore, doc, getDoc, setDoc } from "firebase/firestore";

function App({ event, onChange }) {
  const [state, setState] = useState(event);
  const [images, setImages] = useState([]);
  
  return (
    <div>
      <div>{state.id}</div>
      <div>{state.startDate}</div>
      <div>{state.endDate}</div>
      <div>links: {state.links.length}</div>
      {state.imgdat ? <img src={state.imgdat} /> : null}
      <textarea
        value={state.text}
        onChange={(e) => setState((s) => ({ ...s, text: e.target.value }))}
      />
      <button onClick={() => onChange(state)}>save</button>
      <button onClick={() => {
        fetch(`/images?q=${encodeURIComponent(event.text)}`)
          .then((res) => res.json())
          .then((res) =>
            setImages((s) => (res.imgs))
          )
          .catch((err) => {
            console.error(err);
          });
      }}>get images</button>
      {images.map(img => (<img src={img} onClick={() => setState(s => ({...s, imgdat: img}))} />))}
    </div>
  );
}

export default function ({ eventId }) {
  const [state, setState] = useState(null);

  const reloadDoc = (eventId) =>
    getDoc(doc(getFirestore(), "events", eventId)).then((docSnap) => {
      if (docSnap.exists()) {
        setState(docSnap.data());
      }
    });

  useEffect(() => {
    if (eventId) {
      reloadDoc(eventId);
    }
  }, [eventId]);

  return state == null ? null : (
    <App
      key={state.id}
      event={state}
      onChange={(event) => {
        console.log(event)
        setDoc(doc(getFirestore(), "events", event.id), event).then(() => console.log("saved"))
      }}
    />
  );
}
