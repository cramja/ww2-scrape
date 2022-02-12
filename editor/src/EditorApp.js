import React, { useState, useEffect } from "react";
import { getFirestore, doc, getDoc, setDoc } from "firebase/firestore";

import "./editorApp.css";

function Keywords({ value, onChange }) {
  const [state, setState] = useState(value);
  useEffect(() => {
    onChange(state);
  }, [state]);

  return (
    <div className="editorApp_keywords">
      {state.map((v, i) => (
        <div key={i}>
          <button
            onClick={() =>
              setState((s) => {
                const rv = [...s];
                rv.splice(i, 1);
                return rv;
              })
            }
          >
            x
          </button>
          <input
            value={v}
            onChange={(e) =>
              setState((s) => {
                const rv = [...s];
                rv[i] = e.target.value;
                return rv;
              })
            }
          />
        </div>
      ))}
      <button onClick={() => setState((s) => [...s, ""])}>+</button>
    </div>
  );
}

function Images({ terms, onSelect }) {
  const [query, setQuery] = useState(terms);
  const [images, setImages] = useState([]);

  return (
    <div className="editorApp_images">
      <button
        onClick={() => {
          fetch(`/images?q=${encodeURIComponent(query)}`)
            .then((res) => res.json())
            .then((res) => setImages(res.imgs))
            .catch((err) => console.error(err));
        }}
      >
        search images
      </button>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <div className="editorApp_images_imgs">
        {images.map((img) => (
          <img src={img} onClick={() => onSelect(img)} />
        ))}
      </div>
    </div>
  );
}

function App({ event, onChange }) {
  const [state, setState] = useState(event);

  return (
    <div className="editor_base">
      <div>{state.startDate}</div>
      {state.imgdat ? <img src={state.imgdat} /> : null}
      <Keywords
        value={state.keywords}
        onChange={(keywords) => setState((s) => ({ ...s, keywords }))}
      />
      <textarea
        value={state.text}
        onChange={(e) => setState((s) => ({ ...s, text: e.target.value }))}
      />
      <button onClick={() => onChange(state)}>save</button>
      <Images terms={event.keywords.join(" ")} onSelect={(imgdat) => setState(s => ({...s, imgdat}))}/>
    </div>
  );
}

export default function ({ eventId, onUpdate }) {
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
        event["updateTime"] = new Date().toUTCString();
        setDoc(doc(getFirestore(), "events", event.id), event).then(() =>
          onUpdate(event)
        );
      }}
    />
  );
}
