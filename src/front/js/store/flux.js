const getState = ({ getStore, getActions, setStore }) => {
    return {
        store: {
            message: null,
            datos: [],
            demo: [
                {
                    title: "FIRST",
                    background: "white",
                    initial: "white"
                },
                {
                    title: "SECOND",
                    background: "white",
                    initial: "white"
                }
            ]
        },
        actions: {
            exampleFunction: () => {
                getActions().changeColor(0, "green");
            },

            getMessage: async () => {
                try {
                    const resp = await fetch(process.env.BACKEND_URL + "/api/hello");
                    const data = await resp.json();
                    setStore({ message: data.message });
                    return data;
                } catch (error) {
                    console.log("Error loading message from backend", error);
                }
            },

            changeColor: (index, color) => {
                const store = getStore();
                const demo = store.demo.map((elm, i) => {
                    if (i === index) elm.background = color;
                    return elm;
                });
                setStore({ demo: demo });
            },
            login: async ({ email, password }) => {
				try {
					const response = await fetch(process.env.BACKEND_URL + '/api/login', {

						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
							'accept': 'application/json',

						},
						body: JSON.stringify({ 'email': email, 'password': password })
					});

					if (!response.ok) {
						console.error('Error al enviar datos');
						throw new Error('Error al enviar datos');
					}

					const data = await response.json();
					localStorage.setItem("jwt-token", data.token);
					setStore({ currentUser: data });
					return true;
				} catch (error) {
					console.error('Error:', error);
					return false;
				}
			},
            registro: async ({ email, password }) => {
                try {
                    const response = await fetch('http://127.0.0.1:3001/api/users', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'accept': 'application/json'
                        },
                        body: JSON.stringify({ 'email': email, 'password': password }) // Enviar contraseña en texto plano
                    });

                    if (!response.ok) {
                        console.error('Error al enviar datos');
                        throw new Error('Error al enviar datos');
                    }

                    const data = await response.json();
                    console.log(data);
                    return data;
                } catch (error) {
                    console.error('Error:', error);
                    throw error;
                }
            },

            forgotPassword: async (email) => {
                try {
                    const response = await fetch('http://127.0.0.1:3001/api/forgot-password', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ email })
                    });

                    if (!response.ok) {
                        console.error('Error al enviar datos');
                        throw new Error('Error al enviar datos');
                    }

                    const data = await response.json();
                    console.log('Correo de recuperación enviado:', data);
                } catch (error) {
                    console.error('Error:', error);
                }
            },

            resetPassword: async (password, user_uuid) => {
                try {
                    const response = await fetch('http://127.0.0.1:3001/api/reset-password/', {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            //'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({ password, user_uuid })
                    });

                    if (!response.ok) {
                        console.error('Error al enviar datos');
                        throw new Error('Error al enviar datos');
                    }

                    const data = await response.json();
                    console.log('Contraseña restablecida:', data);
                } catch (error) {
                    console.error('Error:', error);
                }
            },
            getToken: () => {
                const token = localStorage.getItem('jwt-token');
                return !!token;
            },

            logout: () => {
                localStorage.clear();
            }
        }
    };
};

export default getState;