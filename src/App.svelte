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
  } from "firebase/firestore";
  import { onMount } from "svelte";

  let foodStart,
    foodDuration = "",
    foodType,
    foodAmount = "";
  let sleepStart, currentSleepDocId;
  let entries = [];
  let isSleeping = false;

  function addFood() {
    const startTimestamp = foodStart ? new Date(foodStart) : serverTimestamp();
    addDoc(collection(db, "entries"), {
      type: "food",
      start: startTimestamp,
      duration: parseInt(foodDuration),
      foodType,
      amount: parseInt(foodAmount),
    });
    foodStart = foodDuration = foodType = foodAmount = ""; // Reset form
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
  }

  function endSleep() {
    const endTimestamp = serverTimestamp();
    isSleeping = false;
    // Update the document with end timestamp
  }

  onMount(() => {
    const q = query(collection(db, "entries"), orderBy("start", "desc"));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      entries = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
        start: doc.data().start.toDate(),
      }));
    });
    return () => unsubscribe();
  });
</script>

<main>
  <h1>Tracker</h1>
  <div>
    <button on:click={startSleep} disabled={isSleeping}>Start Sleep</button>
    {#if isSleeping}
      <button on:click={endSleep}>End Sleep</button>
    {/if}
  </div>
  <div>
    <button on:click={() => (foodStart = new Date())}>Start Food Entry</button>
    {#if foodStart}
      <input
        type="number"
        bind:value={foodDuration}
        placeholder="Duration (min)"
      />
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
        {#if entry.duration}Duration: {entry.duration} minutes{/if}
        {#if entry.amount}Amount: {entry.amount}{/if}
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
