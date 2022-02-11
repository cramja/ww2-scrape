import React, { useState } from "react";

export default function ImageScraper({}) {
  const [state, setState] = useState({ state: "idle", imgdat: [] });
  return (
    <div>
      <button
        disabled={state.state == "inprogress"}
        value={state.state == "inprogress" ? "running..." : "scrape"}
        onClick={() => {
          setState((s) => ({ ...s, state: "inprogress" }));
          fetch(
            `/images?q=${encodeURIComponent(
              "standard poodle"
            )}`
          )
            .then((res) => res.json())
            .then((res) =>
              setState((s) => ({ ...s, state: "idle", imgdat:  res.imgs}))
            )
            .catch((err) => {
              console.error(err);
              setState((s) => ({
                ...s,
                state: "idle"
              }));
            });
        }}
      />
      <div>{
        state.imgdat.map(img => (<img src={img} />))}</div>
    </div>
  );
}
