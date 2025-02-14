# MAUP Analysis Tool - Paris Region Logistics

An interactive web application demonstrating the Modifiable Areal Unit Problem (MAUP) through analysis of logistics warehouse distribution in the Paris region.

## Features

- Interactive grid-based spatial analysis
- Multiple socioeconomic indicators visualization
- Dynamic statistical comparisons
- MAUP effect demonstration through adjustable grid sizes
- Simulated Paris region data

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install streamlit pandas numpy scipy folium streamlit-folium branca
```

## Running the Application

```bash
streamlit run main.py
```

The application will be available at http://localhost:5000

## Security Notes

This application uses simulated data and requires no API keys or sensitive credentials. If you plan to extend the application with real data or external services:

1. Never commit sensitive credentials to version control
2. Use environment variables or Streamlit's secrets management for sensitive data
3. Review the .gitignore file to ensure sensitive files are excluded
4. Follow security best practices when handling real socioeconomic data

## Data Sources

The application uses simulated data based on typical patterns in the Paris region. The data generation logic can be found in `data_generator.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details

## References

- Openshaw, S. (1984). The modifiable areal unit problem. Geo Books, Norwich.
- INSEE - Institut National de la Statistique et des Études Économiques
- Fotheringham, A.S. & Wong, D.W.S. (1991). The modifiable areal unit problem in multivariate statistical analysis.
