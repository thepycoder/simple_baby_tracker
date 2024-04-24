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

<main class="container mt-5">
  <h1 class="text-center mb-4">Lio's Activities Tracker</h1>
  <div class="row justify-content-center">
    <section class="col-md-6 mb-3">
      <button
        on:click={startSleep}
        class="btn btn-primary w-100"
        disabled={isSleeping}>Start Sleep</button
      >
      {#if isSleeping}
        <button on:click={endSleep} class="btn btn-danger w-100 mt-2"
          >Stop Sleep</button
        >
        <p class="text-muted text-center mt-2">
          Lio has been sleeping for {formatTime(sleepDuration)}.
        </p>
      {/if}
    </section>
    <section class="col-md-6 mb-3">
      <button
        on:click={startFood}
        class="btn btn-primary w-100"
        disabled={isEating}>Start Food Entry</button
      >
      {#if isEating}
        <div class="input-group mt-2">
          <select bind:value={foodType} class="form-select">
            <option value="">Select Food Type</option>
            <option value="formula">Infant Formula</option>
            <option value="solid">Solid Food</option>
          </select>
          <input
            type="number"
            bind:value={foodAmount}
            class="form-control"
            placeholder="Amount"
          />
        </div>
        <button on:click={endFood} class="btn btn-success w-100 mt-2"
          >Log Food Entry</button
        >
      {/if}
    </section>
  </div>
  <div class="row justify-content-center">
    {#each entries as entry}
      <div class="col-md-8 col-lg-6 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">
              {#if entry.type === "food"}
                <i class="bi bi-cup-straw"></i> Food - {entry.amount}ml
              {:else if entry.type === "sleep"}
                <i class="bi bi-moon-stars"></i> Sleep
              {/if}
            </h5>
            <p class="card-text">Start: {entry.start.toLocaleString()}</p>
            {#if entry.duration}
              <p class="card-text">Duration: {entry.duration} minutes</p>
            {/if}
            {#if entry.end}
              <p class="card-text">End: {entry.end.toLocaleString()}</p>
            {/if}
          </div>
        </div>
      </div>
    {/each}
  </div>
</main>

<style>
  :global(.isSleeping) {
    background-color: #e3f2fd; /* Light blue */
  }
  :global(.isEating) {
    background-color: #e8f5e9; /* Light green */
  }
</style>
