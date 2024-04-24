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

<main>
  <h1>
    LIO {#if isSleeping}is aan het slapen{/if}
    {#if isEating}is aan het eten{/if}
  </h1>
  <div>
    <button on:click={startSleep} disabled={isSleeping}>Start Slaapje</button>
    {#if isSleeping}
      <button on:click={endSleep}>Stop Slaapje</button>
      <p>Lio slaapt al {formatTime(sleepDuration)}.</p>
    {/if}
  </div>
  <div>
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
