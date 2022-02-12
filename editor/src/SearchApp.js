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

import "./searchApp.css";

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

export default function SearchApp({event, onSelect}) {
  const [state, setState] = useState({
    startDate: "1939-08-01",
    endDate: "1939-10-01",
    events: [],
  });

  useEffect(() => {
    if (event != null) {
      setState((state) => {
        const nextEvents = [];
        for (let i = 0; i < state.events.length; i++) {
          if (state.events[i].id == event.id) {
            nextEvents.push(event);
          } else {
            nextEvents.push(state.events[i]);
          }
        }
        return ({...state, events: nextEvents});
      });
    }
  }, [event]);

  useEffect(() => {
    // TODO: pagination
    const q = query(
      collection(getFirestore(), "events"),
      where("startDate", ">=", state.startDate),
      where("startDate", "<=", state.endDate),
      orderBy("startDate", "asc"),
      orderBy("id", "desc"),
      limit(100)
    );
    getDocs(q).then((docs) => {
      const events = [];
      docs.forEach((e) => events.push(e.data()));
      setState((s) => ({ ...s, events }));
    });
  }, [state.endDate, state.startDate]);

  function eventsByDate() {
    const byDate = state.events.reduce((acc, e) => {
            if (!acc[e.startDate]) {
              acc[e.startDate] = [e]
            } else {
              acc[e.startDate].push(e)
            }
            return acc;
          }, {});
    return Object.keys(byDate).sort().map(date => ({date, events: byDate[date]}));
  }

  return (
    <div className="searchApp_base">
      <div className="searchApp_controls">
        <DatePicker
          value={state.startDate}
          onChange={(startDate) => setState((s) => ({ ...s, startDate }))}
        />
        <DatePicker
          value={state.endDate}
          onChange={(endDate) => setState((s) => ({ ...s, endDate }))}
        />
        {state.events.length}
      </div>
      <div className="searchApp_eventList">
        {eventsByDate().map((edate) => {
          return (
            <div className="searchApp_eventGroup">
              <h3>{edate.date}</h3>
              {edate.events.map((e) => (
                <div className="searchApp_event" onClick={() => onSelect(e.id)}>
                  <div className="searchApp_eventMeta">
                    <pre>{e.id}</pre>
                    <pre>{e.updateTime ? "✅" : ""}</pre>
                  </div>
                  <a title={e.text}>{e.text}</a>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}