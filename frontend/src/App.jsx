import { useEffect, useState } from 'react'
import api from './api'
function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [loginError, setLoginError] = useState("")

  const [contacts, setContacts] = useState([])
  const [form, setForm] = useState({ name: '', phone: '', email: '', city: '' })

  useEffect(() => {
    if (!token) return
    async function loadContacts() {
      try {
        const response = await api.get('./api/v1/contacts')
        setContacts(response.data.data)
      }
      catch (error) {
        console.log("Error in getting Contacts", error)
      }
    }
    loadContacts()
  }, [token])

  async function handleLogin(e) {
    e.preventDefault()
    setLoginError("")
    try {
      const response = await api.post('/login', {username, password})
      const newToken = response.data.token
      localStorage.setItem('token', newToken)
      setToken(newToken)
      setUsername("")
      setPassword("")
    } catch (error) {
      setLoginError("Username or Password is wrong!")
    }
  }

  function handleLogout() {
    localStorage.removeItem('token')
    setToken(null)
    setContacts([])
  }

  async function addContact() {
    const { name, phone, email, city } = form
    if (!name || !phone || !email || !city) return
    try {
      const response = await api.post('/api/v1/contacts', {
        name,
        phone,
        email,
        city
      })
      setContacts(prev => [...prev, response.data])
      setForm({ name: '', phone: '', email: '', city: '' })
    } catch (error) {
      console.log("Error in add: ", error)
    }
  }

  async function deleteContact(id) {
    try {
      await api.delete(`/api/v1/contacts/${id}`)
      setContacts(prev => prev.filter(contact => contact.id !== id))
    } catch (error) {
      console.log("Error in Delete: ", error)
    }
  }
  
  if (!token) {
    return (
      <div style={{ padding: 20, maxWidth: 400, margin: "0 auto" }}>
        <h1>Login</h1>
          <form onSubmit={handleLogin}>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder='Username'
              style={{ display: 'block', padding: 8, marginBottom: 10, width: "100%" }}
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder='Password'
              style={{ display: 'block', padding: 8, marginBottom: 10, width: "100%" }}
            />
            <button type="submit" style={{ width: "100%", padding: 8 }}>Login</button>
            {loginError && <p style={{ color: 'red' }}>{loginError}</p>}
          </form>
      </div>
    )
  }
  
  return (
    <div style={{ padding: 20, maxWidth: 500, margin: "0 auto" }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: "center"}}>
        <h1>Contact Manager</h1>
        <button onClick={handleLogout}>Logout</button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20 }}>
        <input
          placeholder="Name"
          value={form.name}
          onChange={e => setForm({ ...form, name: e.target.value })}
        />
        <input
          placeholder="Phone"
          value={form.phone}
          onChange={e => setForm({ ...form, phone: e.target.value })}
        />
        <input
          placeholder="Email"
          value={form.email}
          onChange={e => setForm({ ...form, email: e.target.value })}
        />
        <input
          placeholder="City"
          value={form.city}
          onChange={e => setForm({ ...form, city: e.target.value })}
        />
        <button onClick={addContact}>Add Contact</button>
      </div>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {contacts.map(contact => (
          <li key={contact.id} style={{
            padding: 10,
            borderBottom: "1px solid #eee",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
<div>
              <strong>{contact.name}</strong> — {contact.phone}<br />
              <small>{contact.email} | {contact.city}</small>
            </div>
            <button onClick={() => deleteContact(contact.id)}>Delete</button>
          </li>
        ))}
      </ul>
      <div style={{ marginTop: 20, color: "#666" }}>
        <p>Total contacts: {contacts.length}</p>
      </div>
    </div>
  )
}
export default App
