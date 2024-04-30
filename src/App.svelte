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
    deleteDoc,
  } from "firebase/firestore";
  import { formatTime, formatCardTime } from "./utils";
  import { onMount, onDestroy } from "svelte";
  import { auth, googleProvider } from "./firebase";
  import { authState } from "rxfire/auth";
  import { signInWithPopup, signOut } from "firebase/auth";
  import ConfirmModal from "./ConfirmModal.svelte";
  import SleepEntry from "./SleepEntry.svelte";
  import FoodEntry from "./FoodEntry.svelte";

  const db_table = "dev_entries";
  let foodType = "formula";
  let foodAmount = "200";
  let sleepStart, currentSleepDocId, foodStart, currentFoodDocId;
  let entries = [];
  let isSleeping = false;
  let isEating = false;
  let clockSleepInterval;
  let clockFoodInterval;
  let sleepDuration = 0;
  let eatDuration = 0;
  let lastFoodStart, lastSleepEnd;
  let foodSinceLast = "N/A";
  let sleepSinceLast = "N/A";
  let user = "";

  const unsubscribe = authState(auth).subscribe((u) => (user = u));

  function login() {
    signInWithPopup(auth, googleProvider);
  }

  function logout() {
    signOut();
  }

  // Functionality additions and modifications:
  function toggleFoodType(type) {
    console.log("Food Type: " + type);
    foodType = type;
  }

  // Enhanced local display functions
  function startFood() {
    const startTimestamp = serverTimestamp();
    foodStart = new Date();
    isEating = true;
    addDoc(collection(db, db_table), {
      type: "food",
      subtype: foodType,
      start: startTimestamp,
      amount: foodAmount,
    }).then((docRef) => {
      currentFoodDocId = docRef.id;
      startFoodClock();
    });
  }

  function endFood() {
    const endTimestamp = serverTimestamp();
    if (currentFoodDocId) {
      updateDoc(doc(db, db_table, currentFoodDocId), {
        amount: foodAmount,
        end: endTimestamp,
      }).then(() => {
        lastFoodStart = new Date();
        resetFood();
        updateFoodSinceLast();
      });
    }
  }

  function startSleep() {
    const startTimestamp = serverTimestamp();
    sleepStart = new Date();
    isSleeping = true;
    addDoc(collection(db, db_table), {
      type: "sleep",
      start: startTimestamp,
    }).then((docRef) => {
      currentSleepDocId = docRef.id;
      startSleepClock();
    });
  }

  function endSleep() {
    const endTimestamp = serverTimestamp();
    if (currentSleepDocId) {
      updateDoc(doc(db, db_table, currentSleepDocId), {
        end: endTimestamp,
      }).then(() => {
        lastSleepEnd = new Date();
        resetSleep();
        updateSleepSinceLast();
      });
    }
  }

  function updateFoodSinceLast() {
    if (lastFoodStart) {
      const interval = setInterval(() => {
        const now = new Date();
        foodSinceLast = formatTime(now - lastFoodStart);
      }, 1000);
      // onDestroy(() => clearInterval(interval));
    }
  }

  function updateSleepSinceLast() {
    if (lastSleepEnd) {
      const interval = setInterval(() => {
        const now = new Date();
        sleepSinceLast = formatTime(now - lastSleepEnd);
      }, 1000);
      // onDestroy(() => clearInterval(interval));
    }
  }

  function resetSleep() {
    isSleeping = false;
    stopSleepClock();
  }

  function startSleepClock() {
    clearInterval(clockSleepInterval);
    clockSleepInterval = setInterval(updateSleepDuration, 1000);
  }

  function updateSleepDuration() {
    if (isSleeping) {
      const now = new Date();
      const elapsed = now - sleepStart;
      sleepDuration = Math.floor(elapsed);
    }
  }

  function stopFoodClock() {
    clearInterval(clockFoodInterval);
    sleepDuration = 0;
  }

  function resetFood() {
    isEating = false;
    foodType = "formula";
    foodAmount = "200";
    stopFoodClock();
  }

  function startFoodClock() {
    clearInterval(clockFoodInterval);
    clockFoodInterval = setInterval(updateFoodDuration, 1000);
  }

  function updateFoodDuration() {
    if (isEating) {
      const now = new Date();
      const elapsed = now - foodStart;
      eatDuration = Math.floor(elapsed);
    }
  }

  function stopSleepClock() {
    clearInterval(clockFoodInterval);
    sleepDuration = 0;
  }

  function convertToDatetimeLocal(date) {
    const offset = date.getTimezoneOffset() * 60000; // Convert offset to milliseconds
    const localDate = new Date(date.getTime() - offset); // Adjust date to local time
    return localDate.toISOString().slice(0, 16); // Convert to ISO string without 'Z'
  }

  onMount(() => {
    const q = query(
      collection(db, db_table),
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
          edit_start: convertToDatetimeLocal(data.start.toDate()),
          end: data.end ? data.end.toDate() : null,
          edit_end: data.end ? convertToDatetimeLocal(data.end.toDate()) : null,
        };
      });
      // Initialize latest end times
      const lastSleep = entries.find((e) => e.type === "sleep" && e.end);
      const lastFood = entries.find((e) => e.type === "food" && e.start);

      if (lastSleep) {
        lastSleepEnd = lastSleep.end;
        updateSleepSinceLast();
      }
      if (lastFood) {
        lastFoodStart = lastFood.start;
        updateFoodSinceLast();
      }
      // Update current activity states based on the latest entries
      updateCurrentActivities();
    });
    return () => unsubscribe();
  });

  function increaseAmount() {
    foodAmount = (+foodAmount + 10).toString(); // Convert to number, increment, and back to string to handle binding correctly
  }

  function decreaseAmount() {
    if (foodAmount > 10) {
      // Ensure the amount doesn't go negative
      foodAmount = (+foodAmount - 10).toString();
    }
  }

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
        startSleepClock();
      }
    } else if (isSleeping) {
      isSleeping = false;
      stopSleepClock();
    }

    isEating = !!activeFoodEntry;
    if (activeFoodEntry) {
      currentFoodDocId = activeFoodEntry.id;
    }
  }

  let showModal = false;
  let entryIdToDelete = null;

  async function removeEntry(entryId) {
    try {
      await deleteDoc(doc(db, db_table, entryId));
      // Optionally add some UI feedback here, e.g., a toast notification
    } catch (error) {
      console.error("Error removing document: ", error);
      // Handle errors, e.g., show an error message to the user
    }
  }

  function requestDelete(entryId) {
    entryIdToDelete = entryId;
    showModal = true;
  }

  function handleConfirm() {
    removeEntry(entryIdToDelete);
    showModal = false;
    entryIdToDelete = null;
  }

  function handleCancel() {
    showModal = false;
    entryIdToDelete = null;
  }
</script>

<main class="container mt-5">
  <ConfirmModal
    show={showModal}
    message="Are you sure you want to delete this entry?"
    on:confirm={handleConfirm}
    on:cancel={handleCancel}
  />
  {#if user}
    <!-- <h1 class="text-center mb-4">Lio's Activities Tracker</h1> -->
    <div class="row justify-content-center">
      <!-- Sleep input -->
      <section class="col-md-6 mb-3">
        {#if isSleeping}
          <p class="text-muted text-center mt-2">
            Tijd sinds start slaapje: <b class="fs-2"
              >{formatTime(sleepDuration)}</b
            >
          </p>
          <button on:click={endSleep} class="btn btn-danger w-100 mt-2"
            >Stop Sleep</button
          >
        {:else}
          <p class="text-muted text-center mt-2">
            Tijd sinds laatste slaapje: <b class="fs-2">{sleepSinceLast}</b>
          </p>
          <button
            on:click={startSleep}
            class="btn btn-primary w-100 mt-2"
            disabled={isSleeping}>Start Sleep</button
          >
        {/if}
      </section>
      <!-- Food input -->
      <section class="col-md-6 mb-3">
        {#if isEating}
          <p class="text-muted text-center mt-2">
            Aan het eten voor: <b class="fs-2">{formatTime(eatDuration)}</b>
          </p>
          <div class="btn-group mt-2 w-100">
            <button
              on:click={() => toggleFoodType("formula")}
              class={foodType === "formula"
                ? "btn btn-danger"
                : "btn btn-outline-danger"}
              ><i class="bi bi-cup-straw"></i> Infant Formula
            </button>
            <button
              on:click={() => toggleFoodType("solid")}
              class={foodType === "solid"
                ? "btn btn-success"
                : "btn btn-outline-success"}
              ><i class="bi bi-apple"></i> Solid Food
            </button>
          </div>
          <div class="input-group mt-2">
            <button
              class="btn btn-outline-secondary"
              type="button"
              on:click={decreaseAmount}>-10</button
            >
            <input
              type="number"
              bind:value={foodAmount}
              class="form-control"
              placeholder="Hoeveel?"
            />
            <button
              class="btn btn-outline-secondary"
              type="button"
              on:click={increaseAmount}>+10</button
            >
          </div>
          <button on:click={endFood} class="btn btn-success w-100 mt-2"
            >Log Food Entry</button
          >
        {:else}
          <p class="text-muted text-center mt-2">
            Time since last food: <b class="fs-2">{foodSinceLast}</b>
          </p>
          <button
            on:click={startFood}
            class="btn btn-primary w-100 mt-2"
            disabled={isEating}>Start Food Entry</button
          >
        {/if}
      </section>
    </div>
    <div class="row justify-content-center">
      <!-- Latest Sleep entry -->
      <div class="col-md-6">
        {#each entries.filter((e) => e.type === "sleep").slice(0, 1) as entry}
          <SleepEntry {entry} latest={true} onDelete={requestDelete} />
        {/each}
      </div>
      <!-- Latest Food entry -->
      <div class="col-md-6">
        {#each entries.filter((e) => e.type === "food").slice(0, 1) as entry}
          <FoodEntry {entry} latest={true} onDelete={requestDelete} />
        {/each}
      </div>
    </div>
    <div class="row justify-content-center">
      <!-- All Sleep entries excluding the latest -->
      <div class="col-md-6">
        {#each entries.filter((e) => e.type === "sleep").slice(1) as entry}
          <SleepEntry {entry} latest={false} onDelete={requestDelete} />
        {/each}
      </div>
      <!-- All Food entries excluding the latest -->
      <div class="col-md-6">
        {#each entries.filter((e) => e.type === "food").slice(1) as entry}
          <FoodEntry {entry} latest={false} onDelete={requestDelete} />
        {/each}
      </div>
    </div>
  {:else}
    <div class="headerBar">
      <h1 class="header top">Victor's baby tracker!</h1>
      <button on:click={login} class="btn btn-primary"
        >Sign in with google</button
      >
    </div>
  {/if}
</main>
