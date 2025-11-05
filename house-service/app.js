const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// Base de datos en memoria de asignaciones
assigned_houses = [];

// Simular falla aleatoria de la Casa (ej. el Sombrero Seleccionador está ocupado o la Casa llena)
function randomFailure(probability = 0.3) {
  return Math.random() < probability;
}

app.post('/assign', (req, res) => {
  const student = req.body.student;

  if (randomFailure()) {
    // Si falla, el Orquestador ejecutará la compensación (revoke_wand)
    return res.status(500).json({ message: `Error: La Casa de ${student} está llena. Fallo en la asignación.`});
  }

  // Lógica de confirmación: asignar la Casa
  assigned_houses.push(student);
  res.status(200).json({ message:`Estudiante ${student} asignado a una Casa `});
});

app.post('/undo', (req, res) => {
  const student = req.body.student;
  const index = assigned_houses.indexOf(student);
  
  // Lógica de compensación: retirar la asignación
  if (index !== -1) {
    assigned_houses.splice(index, 1);
    res.status(200).json({ message: `Asignación de Casa retirada para ${student}.`});
  } else {
    res.status(404).json({ message: `No había asignación de Casa para ${student}.`});
  }
});

app.get('/status', (req, res) => {
  res.status(200).json(assigned_houses);
});


app.listen(5002, () => {
  console.log('House Service corriendo en puerto 5002'); 
});