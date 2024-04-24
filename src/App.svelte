<!-- src/App.svelte -->
<script>
  import { db } from "./firebase";
  import {
    collection,
    addDoc,
    serverTimestamp,
    query,
    orderBy,
    onSnapshot,
    doc,
    updateDoc,
    limit,
  } from "firebase/firestore";
  import { onMount, onDestroy } from "svelte";

  let foodStart,
    foodType,
    foodAmount = "";
  let sleepStart, currentSleepDocId;
  let entries = [];
  let isSleeping = false;
  let clockInterval;

  function addFood() {
    const startTimestamp = foodStart ? new Date(foodStart) : serverTimestamp();
    addDoc(collection(db, "entries"), {
      type: "food",
      start: startTimestamp,
      foodType,
      amount: parseInt(foodAmount),
    });
    foodStart = foodType = foodAmount = ""; // Reset form
  }

  function startSleep() {
    const startTimestamp = serverTimestamp();
    sleepStart = new Date(); // For local display
    isSleeping = true;
    addDoc(collection(db, "entries"), {
      type: "sleep",
      start: startTimestamp,
    }).then((docRef) => {
      currentSleepDocId = docRef.id; // Store doc id to update later
    });
    startClock();
  }

  function endSleep() {
    const endTimestamp = serverTimestamp();
    updateDoc(doc(db, "entries", currentSleepDocId), {
      end: endTimestamp,
    });
    isSleeping = false;
    stopClock();
  }

  function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    // Creating a padded string for minutes and seconds for uniformity
    const paddedMinutes = String(minutes).padStart(2, "0");
    const paddedSeconds = String(remainingSeconds).padStart(2, "0");

    // Creating the final formatted string
    return `${hours}:${paddedMinutes}:${paddedSeconds}`;
  }

  function startClock() {
    clearInterval(clockInterval);
    clockInterval = setInterval(() => {
      if (isSleeping) {
        const now = new Date();
        const elapsed = now - sleepStart;
        sleepDuration = Math.floor(elapsed / 1000); // Update duration in seconds
      }
    }, 1000);
  }

  function stopClock() {
    clearInterval(clockInterval);
    sleepDuration = 0;
  }

  let sleepDuration = 0;

  onMount(() => {
    const q = query(collection(db, "entries"), orderBy("start", "desc"));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      let foundActiveSleep = false;
      entries = snapshot.docs.map((doc) => {
        const data = doc.data();
        if (data.type === "sleep" && !data.end) {
          if (!foundActiveSleep) {
            // Check if there's an ongoing sleep not yet ended
            isSleeping = true;
            foundActiveSleep = true;
            currentSleepDocId = doc.id;
            sleepStart = data.start.toDate();
            startClock();
          }
        } else if (
          data.type === "sleep" &&
          data.end &&
          doc.id === currentSleepDocId
        ) {
          stopClock(); // Ensure the clock stops if this document is the current sleep session
        }
        return {
          id: doc.id,
          ...data,
          start: data.start ? data.start.toDate() : null,
          end: data.end ? data.end.toDate() : null,
        };
      });
      if (!foundActiveSleep && isSleeping) {
        isSleeping = false; // Update state if no active sleep is found in the latest fetch
      }
    });
    return () => {
      unsubscribe();
      stopClock();
    };
  });
</script>

<main>
  <h1>Tracker</h1>
  <div>
    <button on:click={startSleep} disabled={isSleeping}>Start Sleep</button>
    {#if isSleeping}
      <button on:click={endSleep}>End Sleep</button>
      <p>Lio slaapt al {formatTime(sleepDuration)}.</p>
    {/if}
  </div>
  <div>
    <button on:click={() => (foodStart = new Date())}>Start Food Entry</button>
    {#if foodStart}
      <select bind:value={foodType}>
        <option value="">Select Food Type</option>
        <option value="formula">Infant Formula</option>
        <option value="solid">Solid Food</option>
      </select>
      <input type="number" bind:value={foodAmount} placeholder="Amount" />
      <button on:click={addFood}>Log Food Entry</button>
    {/if}
  </div>
  <ul>
    {#each entries as entry}
      <li>
        Type: {entry.type}, Start: {entry.start.toLocaleString()},
        {#if entry.duration}
          Duration: {entry.duration} minutes{/if}
        {#if entry.amount}
          Amount: {entry.amount}{/if}
        {#if entry.end}
          End: {entry.end.toLocaleString()}{/if}
      </li>
    {/each}
  </ul>
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  div {
    margin-bottom: 20px;
  }
  input,
  select,
  button {
    margin: 5px;
  }
  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    margin-bottom: 10px;
    padding: 5px;
    border: 1px solid #ccc;
  }
</style>
