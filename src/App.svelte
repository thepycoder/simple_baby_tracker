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
    getDoc,
  } from "firebase/firestore";
  import { onMount, onDestroy } from "svelte";

  let foodType,
    foodAmount = "200",
    currentFoodDocId;
  let sleepStart, currentSleepDocId;
  let entries = [];
  let isSleeping = false;
  let isEating = false;
  let clockInterval;
  let sleepDuration = 0;

  // Enhanced local display functions
  function startFood() {
    const startTimestamp = serverTimestamp();
    isEating = true;
    addDoc(collection(db, "entries"), {
      type: "food",
      start: startTimestamp,
      amount: 0, // Initialize with 0 amount
    }).then((docRef) => {
      currentFoodDocId = docRef.id;
    });
  }

  function endFood() {
    const endTimestamp = serverTimestamp();
    if (currentFoodDocId) {
      updateDoc(doc(db, "entries", currentFoodDocId), {
        amount: foodAmount,
        end: endTimestamp,
      }).then(() => resetFood());
    }
  }

  function resetFood() {
    isEating = false;
    foodType = "";
    foodAmount = "";
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

  function startSleep() {
    const startTimestamp = serverTimestamp();
    sleepStart = new Date();
    isSleeping = true;
    addDoc(collection(db, "entries"), {
      type: "sleep",
      start: startTimestamp,
    }).then((docRef) => {
      currentSleepDocId = docRef.id;
      startClock();
    });
  }

  function endSleep() {
    const endTimestamp = serverTimestamp();
    console.log(currentSleepDocId);
    if (currentSleepDocId) {
      updateDoc(doc(db, "entries", currentSleepDocId), {
        end: endTimestamp,
      }).then(() => resetSleep());
    }
  }

  function resetSleep() {
    isSleeping = false;
    stopClock();
  }

  // Clock logic remains similar
  function startClock() {
    clearInterval(clockInterval);
    clockInterval = setInterval(updateSleepDuration, 1000);
  }

  function updateSleepDuration() {
    if (isSleeping) {
      const now = new Date();
      const elapsed = now - sleepStart;
      sleepDuration = Math.floor(elapsed / 1000);
    }
  }

  function stopClock() {
    clearInterval(clockInterval);
    sleepDuration = 0;
  }

  onMount(() => {
    const q = query(
      collection(db, "entries"),
      orderBy("start", "desc"),
      limit(10)
    );
    const unsubscribe = onSnapshot(q, (snapshot) => {
      entries = snapshot.docs.map((doc) => {
        const data = doc.data();
        return {
          id: doc.id,
          ...data,
          start: data.start.toDate(),
          end: data.end ? data.end.toDate() : null,
        };
      });
      // Update current activity states based on the latest entries
      updateCurrentActivities();
    });
    return () => unsubscribe();
  });

  function updateCurrentActivities() {
    let activeSleepEntry = entries.find(
      (entry) => entry.type === "sleep" && !entry.end
    );
    let activeFoodEntry = entries.find(
      (entry) => entry.type === "food" && !entry.end
    );

    if (activeSleepEntry) {
      currentSleepDocId = activeSleepEntry.id;
      sleepStart = activeSleepEntry.start;
      if (!isSleeping) {
        isSleeping = true;
        startClock();
      }
    } else if (isSleeping) {
      isSleeping = false;
      stopClock();
    }

    isEating = !!activeFoodEntry;
    if (activeFoodEntry) {
      currentFoodDocId = activeFoodEntry.id;
    }
  }
</script>

<main class:isEating class:isSleeping>
  <h1>Lio's Activities Tracker</h1>
  <section id="sleep-controls">
    <button on:click={startSleep} disabled={isSleeping}>Start Sleep</button>
    {#if isSleeping}
      <button on:click={endSleep}>Stop Sleep</button>
      <p>Lio has been sleeping for {formatTime(sleepDuration)}.</p>
    {/if}
  </section>
  <section id="food-controls">
    <button on:click={startFood} disabled={isEating}>Start Food Entry</button>
    {#if isEating}
      <select bind:value={foodType}>
        <option value="">Select Food Type</option>
        <option value="formula">Infant Formula</option>
        <option value="solid">Solid Food</option>
      </select>
      <input type="number" bind:value={foodAmount} placeholder="Amount" />
      <button on:click={endFood}>Log Food Entry</button>
    {/if}
  </section>
  <div class="entry-list">
    {#each entries as entry}
      <div class="entry">
        <p>Type: {entry.type}</p>
        <p>Start: {entry.start.toLocaleString()}</p>
        {#if entry.duration}
          <p>Duration: {entry.duration} minutes</p>
        {/if}
        {#if entry.amount}
          <p>Amount: {entry.amount}</p>
        {/if}
        {#if entry.end}
          <p>End: {entry.end.toLocaleString()}</p>
        {/if}
      </div>
    {/each}
  </div>
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  section {
    margin-bottom: 20px;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  input,
  select,
  button {
    margin: 5px;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  .entry-list {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .entry {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 8px;
    background: #f9f9f9;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    width: 90%;
  }
  :global(.isSleeping) {
    background-color: #90caf9; /* Light blue */
    color: #0d47a1; /* Navy blue */
  }
  :global(.isEating) {
    background-color: #a5d6a7; /* Light green */
    color: #1b5e20; /* Dark green */
  }
</style>
