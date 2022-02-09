import React, { useEffect, useState } from "react";

import {
  getFirestore,
  collection,
  query,
  orderBy,
  limit,
  getDocs,
  where,
} from "firebase/firestore";


const isDate = (string) => /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(string);

const trimText = (text) => {
  const limit = 36;
  if (text.length <= limit) {
    return text;
  }
  return text.substring(0, limit - 3).trim() + "...";
};

function DatePicker({ value, onChange }) {
  const [state, setState] = useState({ value, valid: isDate(value) });
  useEffect(() => {
    const valid = isDate(state.value);
    if (valid != state.valid) {
      setState((s) => ({ ...s, valid }));
    }
    if (valid) {
      onChange(state.value);
    }
  }, [state.value]);

  return (
    <div>
      <div>{state.valid ? "" : "!"}</div>
      <input
        placeholder="YYYY-MM-DD"
        value={state.value}
        onChange={(e) =>
          setState((s) => ({ ...s, value: e.target.value.trim() }))
        }
      />
    </div>
  );
}

export default function SearchApp({}) {
  const [state, setState] = useState({
    startDate: "1941-08-01",
    endDate: "1942-01-01",
    events: null,
  });

  useEffect(() => {
    // TODO: pagination
    const q = query(
      collection(getFirestore(), "events"),
      where("startDate", ">=", state.startDate),
      where("startDate", "<=", state.endDate),
      orderBy("startDate", "asc"),
      //orderBy("id", "desc"),
      limit(100)
    );
    getDocs(q).then((docs) => {
      const events = [];
      docs.forEach((e) => events.push(e.data()));
      setState((s) => ({ ...s, events }));
    });
  }, [state.endDate, state.startDate]);

  return (
    <div>
      <div>
        <DatePicker
          value={state.startDate}
          onChange={(startDate) => setState((s) => ({ ...s, startDate }))}
        />
        <DatePicker
          value={state.endDate}
          onChange={(endDate) => setState((s) => ({ ...s, endDate }))}
        />
        {state.events == null ? 0 : state.events.length}
      </div>
      <div>
        {state.events == null
          ? ""
          : state.events.map((e) => (
              <div>
                {e.startDate} - {trimText(e.text)}
              </div>
            ))}
      </div>
    </div>
  );
}