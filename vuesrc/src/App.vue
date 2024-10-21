<template>
  <v-app>
    <v-main>
      <v-select
        v-model="selectedtag"
        :items="tags"
        label="Select tags"
        clearable
      ></v-select>
      <v-chip>New images: {{ incomingImages.length }}</v-chip>
      <v-btn v-if="incomingImages.length > 0" @click="addImages">Refresh</v-btn>
      <v-list>
        <v-list-item v-for="item in (displayedItems as ImageData[])" :key="item">
          {{ item.id  }}
          <v-btn @click="openDialog(item.id)">Show Image</v-btn>
        </v-list-item>
      </v-list>
      <v-pagination
        v-model="currentPage"
        :length="totalPages"
      ></v-pagination>
    </v-main>
    <v-dialog v-model="dialogVisible">
      <v-card>
        <v-card-title>
          Obrazek
        </v-card-title>
        <v-card-text>
          <v-progress-circular v-if="!imageLoaded"
            indeterminate
            color="primary"
          ></v-progress-circular>
          <div id="dialog-text">
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="closeDialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup lang="ts">
  interface ImageData {
    id: number;
    tags: string[];
  };

  import { ref, onMounted, watch, nextTick } from 'vue';

  const items = ref([]);
  const currentPage = ref(1);
  const totalPages = ref(0);
  const displayedItems = ref([]);
  const itemsPerPage = 5;
  const dialogVisible = ref(false);
  const selectedImageId = ref(null); // New data property
  const imageToDisplay = ref(null);
  const imageLoaded = ref(false);
  const incomingImages = ref([] as number[]);
  const tags = ref([]);
  const selectedtag = ref(null);

  let newws = async () => {
    fetchData();
    fetchTags();
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const id = data.id;
      incomingImages.value.push(id as number);
    };
    ws.onerror = () => ws.close();
    ws.onclose = () => {
      setTimeout(() => {
        newws();
      }, 1000);
    };
  };
  onMounted(newws);

  const fetchTags = async () => {
    try {
      const response = await fetch(`http://localhost:8000/tags`);
      const data = await response.json();
      tags.value = data.tags;
    } catch (error) {
      console.error(error);
    }
  }

  const fetchData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/list`);
      const data = await response.json();
      items.value = data;
      totalPages.value = Math.ceil(data.length / itemsPerPage);
      updateList();
    } catch (error) {
      console.error(error);
    }
  };

  const updateList = async () => {
    let filteredItems = items.value;
    if (selectedtag.value) {
      filteredItems = items.value.filter((item: ImageData) => item.tags.includes((selectedtag.value as unknown as string)));
    }
    displayedItems.value = filteredItems.slice((currentPage.value - 1) * itemsPerPage, currentPage.value * itemsPerPage);
  }

  watch(currentPage, updateList);
  watch(selectedtag, updateList);

  const openDialog = (item) => {
    // Open the dialog and set the selectedImageId
    selectedImageId.value = item;
    dialogVisible.value = true;
    imageLoaded.value = false;
    nextTick(() => {
      fetchImage(item);
    });
  }

  const closeDialog = () => {
    // Close the dialog and reset the selectedImageId
    selectedImageId.value = null;
    imageLoaded.value = false;
    dialogVisible.value = false;
  }

  const fetchImage = async (id) => {
    const cardText = document.getElementById('dialog-text');
    if (!cardText) {
      return;
    }
    try {
      const response = await fetch(`http://localhost:8000/image/${id}`);
      const data = await response.json();
      imageToDisplay.value = data;
      const svg = toSVG(data);
      cardText.innerHTML = svg.outerHTML;

    } catch (error) {
      cardText.innerHTML = 'Error';
    }
    imageLoaded.value = true;
  }


  const toSVG = (data : any) => {
    const rectList = data.rectangles;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100');
    svg.setAttribute('height', '100');

    rectList.forEach(rect => {
        const svgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        svgRect.setAttribute('x', rect.leftTop.x.toString());
        svgRect.setAttribute('y', rect.leftTop.y.toString());
        svgRect.setAttribute('width', rect.width.toString());
        svgRect.setAttribute('height', rect.height.toString());
        svgRect.setAttribute('fill', rect.color);
        svg.appendChild(svgRect);
    });
    return svg;
  }

  const addImages = () => {
    incomingImages.value.splice(0);
    fetchData();
  }

</script>
