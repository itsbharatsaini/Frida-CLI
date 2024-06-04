
class Program
{
    static double CalculateCircleArea(double radius)
    {
        return Math.PI * radius * radius;
    }

    static double CalculateSquareArea(double sideLength)
    {
        return sideLength * sideLength;
    }

    double CalculateTriangleArea(double sideA, double sideB, double sideC)
    {
        if (sideA <= 0 || sideB <= 0 || sideC <= 0)
        {
            throw new ArgumentException("Side lengths must be greater than zero.", nameof(sideA));
        }

        double semiPerimeter = (sideA + sideB + sideC) / 2;
        double area = Math.Sqrt(semiPerimeter * (semiPerimeter - sideA) * (semiPerimeter - sideB) * (semiPerimeter - sideC));
        return area;
    }

    static void Main(string[] args)
    {
        double circleArea = CalculateCircleArea(5);
        Console.WriteLine("Area of circle with radius 5: " + circleArea);

        double squareArea = CalculateSquareArea(4);
        Console.WriteLine("Area of square with side length 4: " + squareArea);

        double triangleArea = CalculateTriangleArea(3, 4, 5);
        Console.WriteLine("Area of triangle with sides 3, 4, and 5: " + triangleArea);
    }
}
