import { useState, useEffect } from "react";
import Drawer from '@mui/material/Drawer';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import Stack from '@mui/material/Stack';

import AgricultureIcon from '@mui/icons-material/Agriculture';
import WaterDropIcon from '@mui/icons-material/WaterDrop';

import { createTheme } from "@mui/material/styles";
import { ThemeProvider } from "@mui/material/styles";
import { CssBaseline } from "@mui/material";

import { Gauge } from '@mui/x-charts/Gauge';

const theme = createTheme({
  palette: {
    mode: "dark",
  },
});

import '../styles/App.css'

export default function App() {
  const [task_list_open, setTaskListOpen] = useState(false);
  const [dialog_open, setDialogOpen] = useState(false);
  const [tasks, setTasks] = useState(null);
  const [task_list, setTaskList] = useState(<div>Loading...</div>)
  const [telemetry, setTelemetry] = useState(null);

  const toggleDrawer = (newOpen: boolean) => { setTaskListOpen(newOpen); };
  const toggleDialog = (newOpen: boolean) => { setDialogOpen(newOpen); };

  useEffect(() => {
    async function fetch_tasks() {
      const response = await fetch('http://127.0.0.1:5000/get_tasks');
      const data = await response.json();
      const t = data.data.filter((task) => task.finished === false);
      setTasks(t);
    }

    async function fetch_telemetry() {
      const response = await fetch('http://127.0.0.1:5000/get');
      const data = await response.json();
      
      console.log(data);

      const hum = data.data.find((element) => element.field === 'humidity');
      const temp = data.data.find((element) => element.field === 'temperature');
      setTelemetry([hum.value, temp.value]);
    }

    if (tasks === null) { fetch_tasks(); }
    if (telemetry === null) { fetch_telemetry(); }
  }, [])

  useEffect(() => {
    if (tasks === null) { return; }
    setTaskList(
      <Box sx={{width: 400}} role="presentation" onClick={(e) => { e.preventDefault(); toggleDrawer(false); }}>
        <List>
          {
            tasks === null ? (
              <div>Loading...</div>
            ) : (
              tasks.map((task, idx) => (
                <ListItem key={idx}>
                  <ListItemButton onClick={(e) => { e.preventDefault(); setDialogOpen(true); }}>
                    <ListItemIcon>
                      {task == "koszenie" ? <AgricultureIcon/> : <WaterDropIcon/>}
                    </ListItemIcon>
                    <ListItemText primary={task.type}/>
                  </ListItemButton>
                </ListItem>
              ))           
            )
          }
        </List>
      </Box>
    );
  }, [tasks]);

  return (
    <div>
      <ThemeProvider theme={theme}>
        <CssBaseline/>
        <Dialog onClose={(e) => { toggleDialog(false); }} open={dialog_open}>
          <DialogTitle>Aby podjąć to zadanie udaj się do schowka</DialogTitle>
        </Dialog>

        <Box
          component="img"
          src="public/capture.jpg"
          alt="Example"
          sx={{
            width: 400,
            borderRadius: 2,
            transform: "rotate(90deg)",
          }}
        />

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={{ xs: 1, md: 3 }}>
          <Gauge 
            width={500} 
            height={500} 
            value={telemetry === null ? 0 : telemetry[0]} 
            startAngle={-90} 
            endAngle={90}
            sx={{ fontSize: 40}}
            text={({ value }) => `Humidity: ${value}%`}
          />
          <Gauge 
            width={500} 
            height={500} 
            value={telemetry === null ? 0 : telemetry[1]} 
            startAngle={-90} 
            endAngle={90}
            sx={{ fontSize: 40 }} 
            text={({ value }) => `Temperature: ${value}°C`}
          />
        </Stack>
        <Button onClick={(e) => { e.preventDefault(); toggleDrawer(true); }}>
          Dostępne zadania
        </Button>
        <Drawer open={task_list_open} onClose={(e) => { toggleDrawer(false); }}>
          {task_list}
        </Drawer>
      </ThemeProvider>
    </div>
  );
}