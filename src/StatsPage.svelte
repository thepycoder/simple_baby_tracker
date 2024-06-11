<script>
  import StatsBar from "./StatsBar.svelte";
  import { onMount } from "svelte";
  import {
    collection,
    onSnapshot,
    query,
    where,
    getDocs,
    orderBy,
  } from "firebase/firestore";
  import { db, db_table } from "./firebase";
  import { formatTime } from "./utils";

  let activeHours = [];

  function getTotalActiveHours() {
    const now = new Date();
    const dateCutoff = new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000);
    dateCutoff.setHours(0, 0, 0, 0);

    const q = query(
      collection(db, db_table),
      where("end", ">=", dateCutoff),
      orderBy("end", "desc")
    );

    // We'll use a promise to handle the async nature of the onSnapshot function
    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        let dateToTypeToDuration = new Map();
        snapshot.docs.forEach((doc) => {
          const data = doc.data();
          if (!data.end) {
            return;
          }
          if (data.type == "sleep") {
            console.log(data.start.toDate() + " => ", data.end.toDate());
          }
          let startDate = data.start.toDate();
          let endDate = data.end.toDate();

          const nextMidnight = new Date(startDate);
          nextMidnight.setDate(nextMidnight.getDate() + 1);
          nextMidnight.setHours(0, 0, 0, 0);

          if (nextMidnight < endDate) {
            updateMap(dateToTypeToDuration, data, startDate, nextMidnight);
            updateMap(dateToTypeToDuration, data, nextMidnight, endDate);
          } else {
            updateMap(dateToTypeToDuration, data, startDate, endDate);
          }
        });

        // Convert map to array
        const resultArray = Array.from(
          dateToTypeToDuration,
          ([date, data]) => ({
            date,
            ...data,
          })
        );

        console.log("Activities Array: ", resultArray);
        activeHours = resultArray.slice(1, 59);
      },
      (error) => {
        console.error("Error fetching data: ", error);
        reject(error); // Reject the promise in case of error
      }
    );
  }

  function updateMap(dateToTypeToDuration, data, startDate, currentEndDate) {
    const duration = currentEndDate - startDate;
    const dateString = startDate.toLocaleDateString("nl-BE", {
      year: "numeric",
      month: "long",
      day: "numeric",
      weekday: "long",
    });
    const dateKey = dateString.charAt(0).toUpperCase() + dateString.slice(1);

    if (!dateToTypeToDuration.has(dateKey)) {
      dateToTypeToDuration.set(dateKey, {
        [data.type]: duration,
        [data.type + "Count"]: 1,
        [data.type + "SolidAmount"]:
          data.subtype == "solid" ? Number(data.amount) || 0 : 0, // Initialize amount if it exists
        [data.type + "FormulaAmount"]:
          data.subtype == "formula" ? Number(data.amount) || 0 : 0, // Initialize amount if it exists
      });
    } else {
      const dateData = dateToTypeToDuration.get(dateKey);
      dateData[data.type] = (dateData[data.type] || 0) + duration;
      dateData[data.type + "Count"] = (dateData[data.type + "Count"] || 0) + 1;

      if (data.amount) {
        if (data.subtype == "solid") {
          // Add the amount if it exists
          dateData[data.type + "SolidAmount"] =
            (dateData[data.type + "SolidAmount"] || 0) + Number(data.amount);
        } else if (data.subtype == "formula") {
          // Add the amount if it exists
          dateData[data.type + "FormulaAmount"] =
            (dateData[data.type + "FormulaAmount"] || 0) + Number(data.amount);
        }
      }

      dateToTypeToDuration.set(dateKey, dateData); // Update the map entry
    }
  }

  onMount(() => {
    getTotalActiveHours();
  });
</script>

<div class="container">
  <div class="row mb-2 mt-4 justify-content-center">
    <StatsBar />
  </div>
  {#each activeHours as count}
    <div class="row mb-2 justify-content-center">
      <div class="col-md-6 text-center">
        <div class="card">
          <h5 class="card-header">{count.date}</h5>
          <div class="card-body row">
            <div class="col-6 text-center border-end">
              <h1 class="d-inline">{formatTime(count.sleep)}</h1>
              <small> Geslapen</small>
              <br />
              <span class="text-muted">{count.sleepCount} dutjes in totaal</span
              >
            </div>
            <div class="col-6 text-center">
              <h1 class="d-inline">{count.foodCount}</h1>
              <small> Voedingen</small>
              <br />
              <span class="text-muted"
                >{count.foodFormulaAmount || 0} ml + {count.foodSolidAmount ||
                  0} gr</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  {/each}
</div>
